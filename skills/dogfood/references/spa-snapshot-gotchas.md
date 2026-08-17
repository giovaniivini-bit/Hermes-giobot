# SPA Snapshot Gotchas — Case Studies

## Case 1: Counter Zero-Fill in Card-Based SPA

**Scenario:** Task management app (React SPA) with user cards showing pending-task counts.

**Snapshot showed:** Every card had `StaticText "0"` for the counter value.

**Visual reality (browser_vision):** Ketlyn=11, Ariel=12, Giovani=16, Hering=7.

**Why it happens:** The accessibility tree can render placeholder/initial-state values while the actual React component state has the real data. Snapshot captures DOM structure (including Angular/React hydration placeholders), not the fully rendered visual.

**Fix:** Never report numeric counters from `browser_snapshot` alone. Always cross-check with `browser_vision(question="What numbers are shown on each card?")` before presenting data to the user.

---

## Case 2: Expansion-Attribution Mismatch

**Scenario:** Clicking a user card to expand their task list. Clicked "Giovani" (ref=e19).

**Snapshot showed:** Expanded content (tasks, checkboxes, observations) appearing under "Ketlyn" (ref=e13) in the accessibility tree, with "11" as the counter — even though it was "Giovani" that was visually expanded.

**Visual reality (browser_vision):** "Giovani" card was indeed expanded with his own tasks showing.

**Why it happens:** The accessibility tree may append expanded content at the position of the first card that was ever expanded in the session, rather than at the currently-expanded card's position in the tree. The text snapshot reflects structural DOM ordering, not visual z-order or state.

**Fix:** 
1. After every expand click, call `browser_vision(question="Who is expanded? What content is visible?")` to confirm which card actually opened.
2. Do not trust the heading name under which task items appear in the snapshot — the tree can misattribute them.
3. Before reporting "this user has X tasks," verify the card header visually.

---

## Case 3: Blank-Page After Return Navigation

**Scenario:** Navigating to the main URL after a previous interaction, then fetching a snapshot.

**Snapshot showed:** `"(empty page)"` with `element_count: 0`.

**Visual reality (browser_vision):** Page was fully rendered with all cards visible.

**Why it happens:** The headless browser's accessibility tree may not have populated by the time the snapshot is taken after a SPA navigation. The SPA's async rendering cycle (router transitions, data fetching) can complete visually before the accessibility tree updates.

**Fix:** When `browser_snapshot` returns empty, check `browser_vision` before concluding the page is broken or empty. If vision shows a real page, re-try the snapshot or proceed with vision-based interaction.

---

## Case 4: SPA Modal Form — Accessible Tree Hides Fields

**Scenario:** A task management SPA with a modal form ("Nova Pendência"). Clicking the "+" button opens a modal overlay with text input, textarea, and submit button. The modal content is NOT visible in the accessibility tree snapshot at all — the snapshot shows only the underlying page.

**Visual reality (browser_vision):** The modal is fully visible with title "Nova Pendência (Giovani)" and all form fields accessible visually.

**Why it happens:** The modal may be rendered outside the main DOM tree (portal, separate React tree, or inside a shadow DOM that the snapshot tool doesn't traverse). The accessibility tree captures the top-level DOM only.

**Programmatic form-filling strategy (when browser_type can't reach the fields):**

```javascript
// Step 1: Fill field with proper framework event triggering
var input = document.getElementById('task-text');
var nativeSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeSetter.call(input, 'teste Hermes');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));

// Step 2: Submit the parent form (more reliable than button.click())
var form = input.closest('form');
form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
```

**Why nativeSetter + events:**
- `element.value = 'text'` does not trigger framework change detection (React/Vue/Svelte listen on synthetic events, not property assignment).
- `input.dispatchEvent(new Event('input', ...))` triggers the framework's change handlers.
- Button `.click()` may silently fail if the button's onClick handler is attached via framework data bindings rather than a DOM event listener. Dispatching `submit` on the `<form>` element bypasses this and triggers the component's form submission handler directly.

**Alternative — keyboard Enter:**
If the field is focused, `browser_press(key="Enter")` may also trigger submission depending on the framework's keydown handling. Prefer form.submit() dispatch for reliability.

**Fix:**
1. Use `browser_vision` to confirm the modal is open and to read field content/values.
2. Fill fields programmatically via `browser_console` with the nativeSetter pattern above.
3. Submit via `form.dispatchEvent(new Event('submit', ...))` rather than clicking buttons.
4. Verify success visually: `browser_vision` should show the modal closed, possibly with a success toast/alert.
