import { chromium } from "playwright-core";

const baseUrl = process.env.CUA_GYM_URL ?? "http://127.0.0.1:5173";
const adminToken = process.env.CUA_GYM_ADMIN_TOKEN ?? "skillforge-pilot";
const chromePath =
  process.env.CHROME_PATH ?? "/usr/local/bin/google-chrome";

const initialState = {
  user: {
    id: "u1",
    username: "SkillForge Pilot",
    email: "pilot@example.com",
    avatar: "",
  },
  calendars: [
    {
      id: "c1",
      name: "Personal",
      color: "#039BE5",
      visible: true,
      userId: "u1",
      isDefault: true,
    },
  ],
  otherCalendars: [],
  events: [],
  view: "week",
  currentDate: "2026-08-10T00:00:00.000Z",
  sidebarOpen: true,
  settings: {
    weekStart: 0,
    defaultDuration: 60,
    defaultView: "week",
    defaultReminder: { type: "popup", minutes: 10 },
    timeFormat: "12h",
    showWeekNumbers: false,
    showDeclinedEvents: false,
  },
};

async function adminRequest(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      "x-cua-admin-token": adminToken,
      ...(options.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error(`${options.method ?? "GET"} ${path}: ${response.status}`);
  }
  return response.json();
}

async function createCalendarEvent(page, event) {
  // This is the candidate high-level skill. It sees only the rendered UI.
  let primitiveActions = 0;
  await page.getByRole("button", { name: "Create", exact: true }).click();
  primitiveActions += 1;
  await page.getByPlaceholder("Add title").fill(event.title);
  primitiveActions += 1;
  const dateInputs = page.locator('input[type="datetime-local"]');
  await dateInputs.nth(0).fill(event.start);
  await dateInputs.nth(1).fill(event.end);
  primitiveActions += 2;
  await page.getByPlaceholder("Add location").fill(event.location);
  primitiveActions += 1;
  await page.getByPlaceholder("Add description").fill(event.description);
  primitiveActions += 1;
  await page.getByRole("button", { name: "Save", exact: true }).click();
  primitiveActions += 1;
  return { primitiveActions, skillCalls: 1 };
}

function reward(state, expected) {
  const matching = state.current_state.events.filter(
    (event) =>
      event.title === expected.title &&
      event.start.startsWith(expected.start) &&
      event.end.startsWith(expected.end) &&
      event.location === expected.location &&
      event.description === expected.description,
  );
  return matching.length === 1 ? 1 : 0;
}

const cases = [
  {
    title: "Architecture Review",
    start: "2026-08-10T09:00",
    end: "2026-08-10T10:00",
    location: "Room 3A",
    description: "Review the dynamic skill proposal",
  },
  {
    title: "Customer Follow-up",
    start: "2026-08-11T14:30",
    end: "2026-08-11T15:15",
    location: "Online",
    description: "Discuss pilot feedback",
  },
  {
    title: "Experiment Retrospective",
    start: "2026-08-12T16:00",
    end: "2026-08-12T17:30",
    location: "Lab",
    description: "Audit held-out results",
  },
];

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});

const results = [];
try {
  for (const [index, testCase] of cases.entries()) {
    const sid = `skillforge_calendar_${index}`;
    const setup = await adminRequest(`/post?sid=${sid}`, {
      method: "POST",
      body: JSON.stringify({ action: "set", state: initialState }),
    });
    if (!setup.launch_url) throw new Error("Hardened setup returned no launch_url");
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(new URL(setup.launch_url, baseUrl).href);
    await page.getByRole("button", { name: "Create", exact: true }).waitFor();
    const usage = await createCalendarEvent(page, testCase);
    const state = await adminRequest(`/go?sid=${sid}`);
    results.push({
      case: index,
      title: testCase.title,
      reward: reward(state, testCase),
      ...usage,
    });
    await context.close();
  }
} finally {
  await browser.close();
}

const summary = {
  cases: results.length,
  passed: results.reduce((total, result) => total + result.reward, 0),
  passRate:
    results.reduce((total, result) => total + result.reward, 0) / results.length,
  results,
};
console.log(JSON.stringify(summary, null, 2));
if (summary.passRate !== 1) process.exitCode = 1;
