"""
RE_screenshots.py
==================
Automated Playwright screenshot script for the RE (Risk Elicitation) oTree project (setup -> task -> demographics -> studyend)

Coverage
--------
Runs ONE block of 8 participants (the 2x2x2 design - treatment x incentive x stakes)

HOW TO USE
----------
1. pip install playwright && playwright install chromium
2. Start oTree from the RE project folder:  otree devserver
3. TESTING_MODE = True --> must match settings.py's TESTING_MODE
4. Run

Capture behaviour
-----------------
* oTree's devserver debug panel is hidden on every page (DEBUG_SELECTORS), so
  screenshots stay short vertically.
* shots.take(..., wide=True) widens the viewport to WIDE_VIEWPORT and captures
  the full page - used for the Details popup, which overflows div.otree-body.
* Every skip/next click is preceded by click_outside(), which dismisses any
  open popup (Escape + a click on empty space) so the run never stalls.
"""

import argparse
import json as _json
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


# ===========================================================================
# Config
# ===========================================================================
BASE_URL            = "http://localhost:8000/"
APP_NAME            = "RE"
SESSION_CONFIG_NAME = "states"    # matches SESSION_CONFIGS[0]['name'] in RE's settings.py
NUM_PARTICIPANTS    = 8           # 1 block = PLAYERS_PER_GROUP in setup/__init__.py
MAX_STEPS           = 200
# Output goes directly in the "Risk Elicitation" folder (sibling to RE), per request.
OUT_DIR             = r"/Users/svsalin/Desktop/Risk Elicitation/RE/screenshots"
HEADED              = True
TESTING_MODE        = True

# Normal capture viewport, and the wider one used for shots that would
# otherwise be cropped horizontally (e.g. the Details popup).
VIEWPORT            = {"width": 1440, "height": 1100}
WIDE_VIEWPORT       = {"width": 2000, "height": 1100}

# oTree's devserver debug panel ("Participant / Session / Variables for template"
# block at the bottom) is hidden before every screenshot so shots stay short.
DEBUG_SELECTORS = ", ".join([
    "#otree-debug-info",
    ".otree-debug-info",
    "#debug-info",
    ".debug-info",
    "#otree-debug",
    ".otree-debug",
])

# Elements that count as a "popup is currently open" marker.
POPUP_SELECTORS = [
    "#infoPopup", "#detailsPopup", "#popup", "#overlay",
    ".popup", ".modal.show", ".modal[style*='block']", ".modal-backdrop",
    ".popup-overlay", ".overlay",
]


# ---------------------------------------------------------------------------
# Treatment metadata - mirrors the deterministic 2x2x2 assignment in
# setup/__init__.py's creating_session() for a group of 8 (players[0..7]
# there correspond to id_in_session 1..8 here). color_treatment and
# axis_scale are independent 50/50 coin flips (not part of the 2x2x2 design),
# drawn per participant, so they aren't predictable here and are left out of
# the folder label.
# ---------------------------------------------------------------------------
def treatment_for_slot(id_in_session):
    idx = id_in_session - 1  # 0-indexed, matches players[...] slicing in creating_session()
    treatment = "sequential" if idx < 4 else "simultaneous"
    incentive = "beliefs" if idx in (0, 2, 4, 6) else "choice"
    stakes = "low" if idx in (0, 1, 4, 5) else "high"
    return treatment, incentive, stakes


def treatment_label(id_in_session):
    treatment, incentive, stakes = treatment_for_slot(id_in_session)
    return f"{treatment}_{incentive}_{stakes}stakes"


# ---------------------------------------------------------------------------
# URL / session helpers
# ---------------------------------------------------------------------------
def normalize_url(base_url, maybe_relative):
    return urljoin(base_url.rstrip("/") + "/", maybe_relative)


def unique_participant_links(page, base_url):
    links = page.eval_on_selector_all(
        "a[href]", "els => els.map(e => e.getAttribute('href'))"
    )
    results, seen = [], set()
    for href in links:
        if not href or "/InitializeParticipant/" not in href:
            continue
        full = normalize_url(base_url, href)
        if full not in seen:
            seen.add(full)
            results.append(full)
    return results


def create_session_and_get_links(page, base_url, config_name, expected_links, testing):
    """REST API -> admin page fallback chain."""
    api_url = normalize_url(base_url, "api/sessions")
    try:
        page.goto(base_url, wait_until="domcontentloaded")
        response = page.request.post(
            api_url,
            data=_json.dumps({
                "session_config_name": config_name,
                "num_participants": expected_links,
                "modified_session_config_fields": {"testing": testing},
            }),
            headers={"Content-Type": "application/json"},
        )
        if response.ok:
            body = response.json()
            session_code = body.get("code") or body.get("session_code")
            if session_code:
                lresp = page.request.get(
                    normalize_url(base_url, f"api/sessions/{session_code}/participants")
                )
                if lresp.ok:
                    urls = []
                    for pt in lresp.json():
                        token = pt.get("_url_param") or pt.get("code")
                        if token:
                            urls.append(normalize_url(base_url, f"InitializeParticipant/{token}"))
                    if len(urls) >= expected_links:
                        print(f"  [session] REST API -> {session_code}")
                        return urls[:expected_links]
                page.goto(normalize_url(base_url, f"SessionMonitor/{session_code}"),
                          wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                links = unique_participant_links(page, base_url)
                if len(links) >= expected_links:
                    print(f"  [session] REST API + monitor scrape -> {session_code}")
                    return links[:expected_links]
    except Exception as e:
        print(f"  [session] REST API failed ({e}), trying admin page...")

    for admin_path in ["sessions", "create_session"]:
        try:
            page.goto(normalize_url(base_url, admin_path), wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
            for btn_text in ["Create new session", "Create session", "New session"]:
                btn = page.locator(f"text={btn_text}").first
                if btn.count() > 0:
                    btn.click()
                    page.wait_for_load_state("domcontentloaded")
                    break
            if page.locator("select[name='session_config']").count() > 0:
                page.select_option("select[name='session_config']", config_name)
                page.wait_for_timeout(500)
            filled = False
            for sel in ["input[name='num_participants']", "input[name='num-demo-participants']",
                        "input[name='num_demo_participants']", "input[type='number']"]:
                if page.locator(sel).count() > 0:
                    page.fill(sel, str(expected_links))
                    filled = True
                    break
            if not filled:
                continue
            for sel in ["button[type='submit']", "input[type='submit']",
                        "button:has-text('Create')", "button:has-text('Start')"]:
                if page.locator(sel).count() > 0:
                    page.locator(sel).first.click()
                    break
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            links = unique_participant_links(page, base_url)
            if links:
                print(f"  [session] Admin page /{admin_path}")
                return links[:expected_links]
        except Exception as e:
            print(f"  [session] Admin page /{admin_path} failed ({e})")

    raise RuntimeError(
        f"Could not create a '{config_name}' session with {expected_links} participants.\n"
        f"Create one manually at {normalize_url(base_url, 'sessions')} and rerun."
    )


# ---------------------------------------------------------------------------
# Page label resolution
# ---------------------------------------------------------------------------
def page_label(page):
    # oTree URLs: /p/{code}/{app}/{PageName}/{page_index}/ -> PageName is parts[-2]
    parts = [p for p in urlparse(page.url).path.split("/") if p]
    return parts[-2] if len(parts) >= 2 else "page"


# ---------------------------------------------------------------------------
# Screenshot capture
# ---------------------------------------------------------------------------
HIDE_DEBUG_JS = """
(sel) => {
  const ID = '__shot_hide_debug__';
  let s = document.getElementById(ID);
  if (!s) {
    s = document.createElement('style');
    s.id = ID;
    s.textContent = sel + ' { display: none !important; }';
    (document.head || document.documentElement).appendChild(s);
  }
}
"""


def hide_debug_info(page, selectors=DEBUG_SELECTORS):
    """Inject a style tag hiding oTree's devserver debug panel. Safe to call
    repeatedly - the tag is added once per document."""
    try:
        page.evaluate(HIDE_DEBUG_JS, selectors)
    except Exception:
        pass


@contextmanager
def wide_viewport(page, size=None):
    """Temporarily widen the viewport so wide/absolutely-positioned elements
    (the Details popup) aren't cut off, then restore the original size."""
    previous = page.viewport_size or dict(VIEWPORT)
    try:
        page.set_viewport_size(dict(size or WIDE_VIEWPORT))
        page.wait_for_timeout(250)   # let the layout reflow
        yield
    finally:
        try:
            page.set_viewport_size(dict(previous))
            page.wait_for_timeout(150)
        except Exception:
            pass


def capture_page(page, target, wide=False):
    """wide=False -> tight crop to the oTree content container (default).
    wide=True   -> temporarily widen the viewport and capture the whole page,
                   for content that overflows the narrow container."""
    target.parent.mkdir(parents=True, exist_ok=True)
    hide_debug_info(page)

    if wide:
        with wide_viewport(page):
            hide_debug_info(page)
            try:
                page.screenshot(path=str(target), full_page=True)
                return
            except Exception:
                pass
        page.screenshot(path=str(target), full_page=True)
        return

    for selector in ["div.otree-body", ".the-whole-space", "main", "form",
                      "div.container", "body"]:
        loc = page.locator(selector).first
        if loc.count() > 0:
            try:
                loc.screenshot(path=str(target))
                return
            except Exception:
                pass
    page.screenshot(path=str(target), full_page=False)


INIT_HIDE_DEBUG_JS = """
(() => {
  const CSS = '%s { display: none !important; }';
  const install = () => {
    const ID = '__shot_hide_debug__';
    if (document.getElementById(ID)) return;
    const s = document.createElement('style');
    s.id = ID;
    s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  };
  install();
  document.addEventListener('DOMContentLoaded', install);
})();
""" % DEBUG_SELECTORS


def new_capture_page(browser):
    """A page sized for capture, with the debug panel suppressed on every
    navigation (add_init_script persists across page loads)."""
    page = browser.new_page(viewport=dict(VIEWPORT), device_scale_factor=2)
    try:
        page.add_init_script(INIT_HIDE_DEBUG_JS)
    except Exception:
        pass
    return page


class Shots:
    """Tiny helper that numbers/labels screenshots within one participant run."""
    def __init__(self, out_dir, folder_label):
        self.out_dir = out_dir
        self.folder_label = folder_label
        self.count = 0

    def take(self, page, label, wide=False):
        self.count += 1
        fname = f"{self.count:03d}_{label}.png"
        capture_page(page, self.out_dir / self.folder_label / fname, wide=wide)
        print(f"      -> {fname}")


# ---------------------------------------------------------------------------
# Advance helpers
# ---------------------------------------------------------------------------
def popup_is_open(page):
    for sel in POPUP_SELECTORS:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                return True
        except Exception:
            continue
    return False


def click_outside(page):
    """Close any client-side popup/modal the way a user would: Escape, then a
    click on empty space outside it. The Details popup on Instructions has no
    close button and blocks the skip/next click until it's dismissed."""
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(120)
    except Exception:
        pass

    # If a backdrop element exists, clicking its top-left corner is the most
    # reliable "outside" target.
    for sel in [".modal-backdrop", ".popup-overlay", ".overlay", "#overlay"]:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                loc.click(position={"x": 3, "y": 3}, force=True)
                page.wait_for_timeout(150)
                return
        except Exception:
            continue

    # Otherwise click a neutral point at the far edge of the viewport, which is
    # outside any centred popup but still inside the document.
    vp = page.viewport_size or VIEWPORT
    for x, y in [(6, vp["height"] // 2), (vp["width"] - 6, vp["height"] // 2)]:
        try:
            page.mouse.click(x, y)
            page.wait_for_timeout(120)
        except Exception:
            continue
        if not popup_is_open(page):
            return


def skip_and_wait(page, timeout=10000, dismiss_popup=True):
    """Click the project's own '#skipTestingBtn' (runs the page's skipPage(),
    generically fills anything left, and calls form.submit() directly - this
    bypasses disabled buttons / checkSubmit() dialogs / HTML5 'required' on
    every page in this project, including the multi-screen ones, since it
    submits the underlying <form> regardless of which sub-screen is visible)."""
    if dismiss_popup:
        click_outside(page)

    url_before = page.url
    skip_btn = page.locator("#skipTestingBtn")
    if skip_btn.count() > 0:
        try:
            with page.expect_navigation(wait_until="domcontentloaded", timeout=timeout):
                skip_btn.click()
            return True
        except PlaywrightTimeoutError:
            pass

    # Fallback: no skip button found (shouldn't happen with testing=True) -
    # try a normal Next-like button.
    for selector in ["button.otree-btn-next", "button[type='submit']",
                      "input[type='submit']", "button:has-text('Next')",
                      "button:has-text('Continue')"]:
        loc = page.locator(selector).first
        if loc.count() > 0:
            try:
                with page.expect_navigation(wait_until="domcontentloaded", timeout=timeout):
                    loc.click()
                return True
            except (PlaywrightTimeoutError, PlaywrightError):
                continue
    return page.url != url_before


# ---------------------------------------------------------------------------
# Custom multi-screen/multi-tab handlers
# ---------------------------------------------------------------------------
def handle_instructions(page, shots):
    """Instructions.html: three client-side tabs (Task / Compensation /
    Comprehension Check), with a "Details" popup on the Compensation tab.
    Tab switching and the modal are pure CSS display toggles - no real page
    navigation - so we screenshot each state, then finish with the global
    skip button (which submits the underlying form regardless of which tab
    is currently showing)."""
    shots.take(page, "Instructions_1_Task")

    page.locator('.tab:visible button[data-offset="1"]').first.click()
    page.wait_for_timeout(150)
    shots.take(page, "Instructions_2_Compensation")

    info_btn = page.locator("#infoButton")
    if info_btn.count() > 0:
        info_btn.click()
        page.wait_for_timeout(250)
        # wide=True: the popup is wider than div.otree-body, so a tight crop
        # cuts its right edge off.
        shots.take(page, "Instructions_3_Compensation_DetailsPopup", wide=True)
        click_outside(page)

    page.locator('.tab:visible button[data-offset="1"]:not(#infoButton)').first.click()
    page.wait_for_timeout(150)
    shots.take(page, "Instructions_4_ComprehensionCheck")

    skip_and_wait(page)


def _handle_simultan(page, shots, base_label, order):
    """Shared driver for Payoffs_Together_Simultan_Choice/Belief: three
    client-side screens (chart+table, choice, guess) navigated via onclick
    handlers that call showChoiceScreen()/showGuessScreen()/showChartScreen()
    - not real page loads. `order` is the sequence of (onclick-substring,
    screen-label) pairs to click through, ending on the screen with the real
    (skip-button-driven) submit."""
    shots.take(page, f"{base_label}_1_ChartTable")
    for step_num, (onclick_marker, label) in enumerate(order, start=2):
        btn = page.locator(f'button[onclick*="{onclick_marker}"]:visible').first
        if btn.count() == 0:
            break
        btn.click()
        page.wait_for_timeout(150)
        shots.take(page, f"{base_label}_{step_num}_{label}")
    skip_and_wait(page)


def handle_simultan_choice(page, shots):
    # chart -> choice -> guess (see Payoffs_Together_Simultan_Choice.html)
    _handle_simultan(page, shots, "Payoffs_Together_Simultan_Choice",
                      [("showChoiceScreen", "Choice"), ("showGuessScreen", "Guess")])


def handle_simultan_belief(page, shots):
    # chart -> guess -> choice (see Payoffs_Together_Simultan_Belief.html)
    _handle_simultan(page, shots, "Payoffs_Together_Simultan_Belief",
                      [("showGuessScreen", "Guess"), ("showChoiceScreen", "Choice")])


CUSTOM_HANDLERS = {
    "Instructions": handle_instructions,
    "Payoffs_Together_Simultan_Choice": handle_simultan_choice,
    "Payoffs_Together_Simultan_Belief": handle_simultan_belief,
}


# ---------------------------------------------------------------------------
# Per-participant runner
# ---------------------------------------------------------------------------
def run_participant(page, participant_url, out_dir, folder_label, max_steps):
    page.goto(participant_url, wait_until="domcontentloaded")
    seen_labels = set()
    shots = Shots(out_dir, folder_label)

    for _ in range(max_steps):
        page.wait_for_load_state("domcontentloaded")
        label = page_label(page)

        if label == "InitializeParticipant" or label == "p":
            # Not a real oTree page yet (e.g. straight after goto); just advance.
            if not skip_and_wait(page):
                break
            continue

        if label not in seen_labels:
            seen_labels.add(label)
            handler = CUSTOM_HANDLERS.get(label)
            if handler is not None:
                handler(page, shots)
                continue
            shots.take(page, label)

        url_before = page.url
        if not skip_and_wait(page):
            break
        if page.url == url_before:
            break

        if "OutOfRangeNotification" in page.url or page_label(page) == "OutOfRangeNotification":
            break


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--config", default=SESSION_CONFIG_NAME)
    parser.add_argument("--participants", type=int, default=NUM_PARTICIPANTS)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--out", default=OUT_DIR)
    parser.add_argument("--testing", action="store_true", default=TESTING_MODE)
    parser.add_argument("--no-testing", dest="testing", action="store_false")
    parser.add_argument("--headed", action="store_true", default=HEADED)
    parser.add_argument("--no-headed", dest="headed", action="store_false")
    args = parser.parse_args()

    out_dir = Path(args.out) / APP_NAME
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  RE Screenshot Capture")
    print(f"  Config       : {args.config}   (testing={args.testing})")
    print(f"  Participants : {args.participants}  |  Headed: {args.headed}")
    print(f"  Output       : {out_dir.resolve()}")
    print(f"{'=' * 60}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        setup_page = new_capture_page(browser)

        print(f"Creating session with {args.participants} participant slots...")
        links = create_session_and_get_links(
            page=setup_page, base_url=args.base_url,
            config_name=args.config, expected_links=args.participants,
            testing=args.testing,
        )
        setup_page.close()

        for i in range(args.participants):
            if i >= len(links):
                print(f"  Warning: ran out of links at participant {i + 1}")
                break
            id_in_session = i + 1
            folder = f"participant_{id_in_session:02d}_{treatment_label(id_in_session)}"
            print(f"  [{id_in_session:02d}/{args.participants}] {treatment_label(id_in_session)}")

            run_page = new_capture_page(browser)
            try:
                run_participant(
                    page=run_page,
                    participant_url=links[i],
                    out_dir=out_dir,
                    folder_label=folder,
                    max_steps=args.max_steps,
                )
            except Exception as e:
                print(f"    ! Error on participant {id_in_session}: {e}")
            run_page.close()

        browser.close()

    print(f"\nDone. Screenshots saved to: {out_dir.resolve()}")
    print("Next:  review, then  otree resetdb")


if __name__ == "__main__":
    main()