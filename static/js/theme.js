/* Theme toggle.  P4.2 — closes R-11 / A4.8.
 *
 * PER-VISIT, by the owner's ruling — and per-visit means the choice survives a
 * navigation. D-59: the first implementation stored nothing, so the choice died
 * with the page and a visitor wanting light had to choose it again on all five
 * pages. The decision said per-visit; the implementation delivered per-page; no
 * condition encoded the difference, so nothing caught it.
 *
 * sessionStorage, one key, the theme word only, cleared with the tab. C-21
 * reads "No cookies set by the site. No localStorage of personal data. No
 * fingerprinting." No cookie is set; the storage ban is scoped to PERSONAL
 * DATA, and one word naming a colour scheme identifies nobody. sessionStorage
 * rather than localStorage because the ruling was per-VISIT, and sessionStorage
 * is precisely the storage whose lifetime is a visit.
 *
 * Applying it before first paint is theme-init.js's job, in <head>. This file
 * only reads and writes the choice; it never repaints.
 *
 * Until the visitor presses the button nothing is stored and no attribute is
 * set, so the CSS media query stays in charge — live, so flipping the OS theme
 * with the page open still follows.
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
    var next = currentTheme() === "light" ? "dark" : "light";
    root.setAttribute("data-theme", next);
    try {
      window.sessionStorage.setItem("theme", next);
    } catch (e) {
      /* Storage can throw outright in some privacy modes. The toggle still
         works for this page; it simply will not survive the navigation. A
         theme preference is not worth an exception that breaks the page. */
    }
    reflectState();
  });
})();
