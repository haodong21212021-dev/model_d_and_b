#!/usr/bin/env python3
"""Report which configured model endpoints actually return a chat completion."""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import requests
import yaml


def resolve_config(path: Path) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    while "extends" in config:
        parent_path = (path.parent / config.pop("extends")).resolve()
        parent = yaml.safe_load(parent_path.read_text(encoding="utf-8")) or {}
        merged = dict(parent)
        for key, value in config.items():
            base_value = parent.get(key)
            merged[key] = (
                {**base_value, **value}
                if isinstance(value, dict) and isinstance(base_value, dict)
                else value
            )
        config, path = merged, parent_path
    return config


def probe(entry: tuple[str, str, str, str]) -> dict[str, Any]:
    config_name, model, base_url, api_key = entry
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    result: dict[str, Any] = {
        "config": config_name,
        "model": model,
        "base_url": base_url,
        "usable": False,
    }
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly OK"}],
                "max_tokens": 8,
                "temperature": 0,
            },
            timeout=60,
        )
    except requests.RequestException as error:
        result["error"] = type(error).__name__
        return result

    result["status"] = response.status_code
    try:
        payload = response.json()
    except ValueError:
        result["error"] = "non_json_response"
        return result

    # A Tencent TI gateway can answer 200 with an error envelope, so require a
    # parsed assistant message before treating the endpoint as usable.
    choices = payload.get("choices")
    if response.ok and isinstance(choices, list) and choices:
        content = (choices[0].get("message") or {}).get("content")
        if isinstance(content, str):
            result["usable"] = True
            result["sample"] = content.strip()[:40]
            return result
    error = payload.get("Response", {}).get("Error", {}) if isinstance(payload, dict) else {}
    result["error"] = error.get("Code") or "unexpected_payload"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    entries: dict[str, tuple[str, str, str, str]] = {}
    for config_path in sorted(args.config_root.rglob("*.yaml")):
        try:
            config = resolve_config(config_path)
        except (OSError, yaml.YAMLError, RecursionError):
            continue
        agent = config.get("agent") or {}
        endpoint = agent.get("endpoint") or {}
        base_url = str(endpoint.get("base_url") or "").rstrip("/")
        if base_url and base_url not in entries:
            entries[base_url] = (
                config_path.name,
                str(agent.get("model") or ""),
                base_url,
                str(endpoint.get("api_key") or ""),
            )

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = sorted(
            pool.map(probe, entries.values()),
            key=lambda row: (not row["usable"], row["config"]),
        )

    report = {
        "endpoints_checked": len(results),
        "usable": [row for row in results if row["usable"]],
        "unusable": [row for row in results if not row["usable"]],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "endpoints_checked": report["endpoints_checked"],
                "usable": [row["model"] for row in report["usable"]],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
