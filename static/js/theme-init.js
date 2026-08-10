/* Apply a chosen theme BEFORE first paint.  P4.2 / D-59.
 *
 * This is the only render-blocking script the site loads, and it is deliberate:
 * a theme applied after paint is a visible flash of the wrong theme, which is
 * indistinguishable from a bug. It is loaded from <head> without `defer` for
 * that reason and no other. Keep it tiny.
 *
 * WHY AN EXTERNAL FILE FOR FOUR LINES. The usual form is an inline <script> in
 * <head>. This build refuses that twice over: the INLINE_SCRIPT gate rejects any
 * <script> with a body and no src, and the CSP is script-src 'self' with no
 * 'unsafe-inline', no nonce and no hash. An external file is the only
 * CSP-compliant way to run something before paint here.
 *
 * WHY sessionStorage, AND WHY THAT IS C-21 CLEAN. C-21 reads: "No cookies set
 * by the site. No localStorage of personal data. No fingerprinting." No cookie
 * is set. The storage ban is scoped to PERSONAL DATA, and one word naming a
 * colour scheme is not personal data — it identifies nobody and describes
 * nothing about the visitor beyond a preference they just expressed on screen.
 * sessionStorage rather than localStorage so the choice dies with the tab: the
 * ruling was per-VISIT, and sessionStorage is the storage whose lifetime is
 * exactly a visit.
 *
 * NOTHING IS WRITTEN HERE. This file only reads. If the visitor has expressed
 * no choice, no attribute is set and the prefers-color-scheme media query stays
 * in charge — live, so flipping the OS theme with the page open still works.
 */
(function () {
  "use strict";
  try {
    var theme = window.sessionStorage.getItem("theme");
    if (theme === "light" || theme === "dark") {
      document.documentElement.setAttribute("data-theme", theme);
    }
  } catch (e) {
    /* Storage can throw outright in some privacy modes. The correct fallback is
       to do nothing: the media query decides, which is the same behaviour a
       first-time visitor gets. A theme toggle is not worth an exception that
       breaks the page. */
  }
})();
