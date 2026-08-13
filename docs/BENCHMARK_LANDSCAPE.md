# MockApp Coverage and Real-Application Benchmarks

Date: 2026-08-13

## 1. What the MockApps simulate

CUA-Gym-Hub ships **98** self-contained React applications. The public task
release only exercises **29** of them, with **1,075** tasks. Numbers below are
task counts from the released index; applications marked `--` are built but have
no released tasks.

### Communication and social (18 built)

| Application | Tasks |
|---|---:|
| instagram | 79 |
| outlook_web | 57 |
| microsoft_teams | 45 |
| pinterest | 53 |
| reddit | 30 |
| wechat | 26 |
| slack | 22 |
| gmail | 13 |
| linkedin | 12 |
| twitter | 12 |
| facebook | 8 |
| discord, dingtalk, feishu, weibo, xiaohongshu, zhihu, zoom_web | -- |

### Productivity and documents (16 built)

| Application | Tasks |
|---|---:|
| google_docs | 76 |
| google_sheets | 55 |
| google_calendar | 50 |
| google_drive | 44 |
| monday | 43 |
| trello | 41 |
| notion | 22 |
| jira | 17 |
| airtable, asana, canva, canvas, Canvas-LMS, confluence, lattice, linear, lucidchart, miro, openreview | -- |

### Development and cloud (12 built)

| Application | Tasks |
|---|---:|
| gitlab | 48 |
| postman | 47 |
| github | 15 |
| aliyun, aws_console, azure, circleci, cloudflare, datadog, sentry, vercel, wandb | -- |

### E-commerce and travel (11 built)

| Application | Tasks |
|---|---:|
| instacart | 60 |
| uber_eats | 48 |
| shopify_admin | 16 |
| amazon, amazon_seller, booking_com, ebay, expedia, taobao_seller, tripadvisor, woocommerce | -- |

### Finance and enterprise (20 built)

| Application | Tasks |
|---|---:|
| hubspot | 77 |
| stripe_dashboard | 31 |
| salesforce | 20 |
| adp, bamboohr, clio, coinbase, contractbook, docusign, Expensify, greenhouse, gusto, hubspot_marketing, paypal, quickbooks, robinhood, SAP, ServiceNow, TradingView, workday | -- |

### Analytics and marketing (10 built)

None have released tasks: amplitude, google_ads, google_analytics, hotjar,
klaviyo, looker_studio, mailchimp, meta_ads, mixpanel, tableau.

### Other (9 built)

`mock_websites` carries 8 generic tasks. No tasks for 12306, epic-health,
google_flights, PACS-viewer, westlaw, youtube, Zendesk, zillow.

### Consequence

Every MockApp imitates a **web SaaS product**. None imitates a desktop
application. So a MockApp-induced skill can only be evaluated on a benchmark of
web applications, never on LibreOffice, VS Code, VLC or GIMP.

## 2. Benchmarks that evaluate operation of real applications

Three categories matter, and mixing them is what broke the earlier design.

### 2.1 Real desktop applications

| Benchmark | Tasks | Applications | Platform | Reward |
|---|---:|---|---|---|
| OSWorld / OSWorld-Verified | 369 (361 verified) | LibreOffice Calc/Writer/Impress, VS Code, VLC, GIMP, Chrome, Thunderbird, OS utilities | Ubuntu | programmatic |
| OSWorld 2.0 | 108 | desktop apps plus 31 self-hosted web services, long-horizon | Ubuntu + web | programmatic checkpoints |
| Windows Agent Arena | 154 | VS Code, LibreOffice Calc/Writer, VLC, File Explorer, Edge, Chrome, Settings, Notepad, Paint, Clock, Calculator | Windows | programmatic |
| macOSWorld | 202 | 30 macOS applications | macOS | programmatic |
| MacArena | 421 | OSWorld and macOSWorld ports plus native macOS | macOS | programmatic |
| MacAgentBench | 676 | 25 macOS applications, about 60% GUI+CLI | macOS | rule-based checkpoints |
| WeaveBench | 114 | LibreOffice, GIMP, VS Code, browsers, CLI, hybrid GUI+CLI | Ubuntu | trajectory-aware judge |
| Gym-Anything / CUA-World-Long | 200 long tasks | 200 real installed applications | mixed | VLM checklist judge |

### 2.2 Real web applications, self-hosted and reproducible

| Benchmark | Tasks | Applications | Reward |
|---|---:|---|---|
| WebArena | 812 | real Magento shop and CMS, real self-hosted GitLab, Postmill, OpenStreetMap, offline Wikipedia | programmatic |
| VisualWebArena | 910 | Classifieds plus inherited Shopping and Reddit | programmatic |
| SaaS-Bench | 106 | 23 open-source SaaS systems: OpenProject, Baserow, Metabase, Twenty CRM, Mattermost, ownCloud, OpenEMR, Pretix, Grocy, OnlyOffice, code-server and others | programmatic |
| TheAgentCompany | 175 | GitLab, ownCloud, Plane, RocketChat | deterministic plus LLM |

WebArena is frequently misread as synthetic. It is real open-source software
self-hosted in containers, which is why it is a legitimate transfer target for
web skills.

### 2.3 Real commercial SaaS and live web

| Benchmark | Tasks | Target | Reward |
|---|---:|---|---|
| SCUBA | 300 | Salesforce sandbox | milestone plus task success |
| WorkArena / WorkArena++ | 33 templates / 682 | ServiceNow demo instance | programmatic |
| Online-Mind2Web | 300 | 136 live websites | LLM judge |
| Mind2Web 2 | 130 | live agentic search | agent-as-judge |
| WebVoyager | 643 | 15 live sites | VLM judge |

### 2.4 Explicitly not real-application benchmarks

CUA-Gym-Hub mocks, WebArena-Infinity, InfiniteWeb Arena, MiniWoB++ and WebShop
are synthetic or generated. They are valid training and mechanism-testing
environments and invalid as evidence of real-application ability.

## 3. Application-level overlap with a LibreOffice / VS Code / VLC / GIMP pool

| Benchmark | Calc | Writer | Impress | VS Code | VLC | GIMP |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| OSWorld-Verified | yes | yes | yes | yes | yes | yes |
| MacArena | yes | yes | yes | yes | yes | no |
| Windows Agent Arena | yes | yes | no | yes | yes | no |
| WeaveBench | yes | yes | yes | yes | partial | yes |
| WebArena family | no | no | no | no | no | no |
| SaaS-Bench | no | no | no | browser code-server only | no | no |
| MockApps | no | no | no | no | no | no |

OSWorld-Verified has the strongest overlap and is the natural primary transfer
target for skills mined from the CUA-Gym real desktop pool.

## 4. Implication for this project

Two separable claims, each needing its own source and target:

| Claim | Skill source | Transfer target |
|---|---|---|
| Skills improve real desktop application operation | CUA-Gym `desktop_office` + `desktop`, 8,029 tasks | OSWorld-Verified primary; WAA for Windows; WeaveBench for long-horizon |
| Skills improve real web application operation | MockApps, 1,075 tasks, application-disjoint | WebArena and SaaS-Bench, which are real self-hosted software in matching domains such as GitLab, Magento, project management and CRM |

The second row is what makes MockApp mining scientifically usable: `gitlab_mock`
maps to real self-hosted GitLab in WebArena, `shopify_admin_mock` and
`amazon_mock` to Magento, `monday_mock` and `jira_mock` to OpenProject and Plane,
`salesforce_mock` and `hubspot_mock` to Twenty CRM. A desktop benchmark can never
serve that row.

`SaaS-Bench` is already present on the development host, so the web transfer
target does not require new procurement.

## 5. Verification notes

- MockApp counts were computed directly from the released task index and the Hub
  catalog.
- Benchmark task counts and application lists come from a targeted survey of
  papers and project pages.
- Reported state-of-the-art numbers were excluded here on purpose. Published,
  aggregator and vendor figures disagree substantially for OSWorld 2.0,
  AndroidWorld and Online-Mind2Web because agent harness, step budget and judge
  differ. Any score used in a paper must be taken from the official harness of
  that benchmark.
- Per-application task splits for OSWorld should be re-derived from the
  repository before being quoted, since the survey figures were not
  independently recomputed here.
