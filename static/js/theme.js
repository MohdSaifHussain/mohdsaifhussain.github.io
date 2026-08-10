/* Theme toggle.  P4.2 — closes R-11 / A4.8.
 *
 * SESSION-ONLY, by the owner's ruling. Nothing is stored: no cookie, no
 * localStorage, no fingerprint. C-21 reads "No cookies set by the site. No
 * localStorage of personal data. No fingerprinting." — a theme preference is
 * not personal data, so storing it would have been permitted; it is not stored
 * because persisting it would need the theme applied BEFORE first paint, and
 * the only ways to do that are an inline <script> (refused by the INLINE_SCRIPT
 * gate and by script-src 'self') or a render-blocking request on a page whose
 * LCP is already declared UNMET. A returning visitor is carried by
 * prefers-color-scheme instead, which is what it is for.
 *
 * So this file sets NO attribute until the visitor actually presses the button.
 * Until then the CSS media query is in charge and stays live — flip the OS
 * theme with the page open and the page follows.
 *
 * The toggle is instant. There is no transition and no keyframe here or in the
 * CSS: a theme change is an A3.3-family state swap, and the declared A3 ledger
 * stays at six entries. Animating it would be undeclared motion (C-12).
 */
(function () {
  "use strict";

  var root = document.documentElement;
  var button = document.querySelector("[data-theme-toggle]");
  if (!button) { return; }

  var query = window.matchMedia("(prefers-color-scheme: light)");

  /* What the visitor is looking at right now: an explicit choice if one has
     been made this visit, otherwise whatever the system asked for. */
  function currentTheme() {
    return root.getAttribute("data-theme") || (query.matches ? "light" : "dark");
  }

  function reflectState() {
    button.setAttribute("aria-pressed", currentTheme() === "light" ? "true" : "false");
  }

  /* Offered only once it can actually do something. */
  button.hidden = false;
  reflectState();

  /* If the OS flips while the page is open and the visitor has not chosen,
     the page changes underneath them — so the control must not go on claiming
     the old state. */
  if (typeof query.addEventListener === "function") {
    query.addEventListener("change", reflectState);
  }

  button.addEventListener("click", function () {
    root.setAttribute("data-theme", currentTheme() === "light" ? "dark" : "light");
    reflectState();
  });
})();
