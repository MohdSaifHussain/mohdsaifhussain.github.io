/* Applies the visitor's per-visit display choices BEFORE first paint.  P4.2,
 * extended by P5.7 with the contrast choice.
 *
 * Runs in <head>, render-blocking on purpose: deferred, it would repaint after
 * the page is on screen, a visible flash of the wrong theme (ruling 4.2.7's
 * accepted cost). Reads two words from sessionStorage and sets two attributes.
 * Nothing else. If storage throws (some privacy modes) it does nothing, and the
 * media queries decide, which is exactly a first-time visitor's experience.
 */
(function () {
  "use strict";
  try {
    var theme = window.sessionStorage.getItem("theme");
    if (theme === "light" || theme === "dark") {
      document.documentElement.setAttribute("data-theme", theme);
    }
    var contrast = window.sessionStorage.getItem("contrast");
    if (contrast === "more" || contrast === "normal") {
      document.documentElement.setAttribute("data-contrast", contrast);
    }
  } catch (e) {
    /* Storage unavailable: the media queries decide. A display preference is
       not worth an exception that breaks the page. */
  }
})();
