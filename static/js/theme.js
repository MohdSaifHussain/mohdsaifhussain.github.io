/* Display toggles: colour theme (P4.2) and contrast (P5.7).
 *
 * PER-VISIT, by the owner's ruling, and per-visit means the choice survives a
 * navigation (D-59). sessionStorage, two keys, one word each, cleared with the
 * tab. C-21 reads "No cookies set by the site. No localStorage of personal
 * data. No fingerprinting." No cookie is set; the storage ban is scoped to
 * PERSONAL DATA, and a word naming a colour scheme or a contrast preference
 * identifies nobody.
 *
 * Applying a choice before first paint is theme-init.js's job. This file only
 * reads and writes the choice; it never repaints.
 *
 * Until the visitor presses a button nothing is stored and no attribute is
 * set, so the CSS media queries stay in charge, live: flipping the OS theme or
 * the OS "increase contrast" setting with the page open still follows.
 *
 * Both toggles are instant: no transition, no keyframe (A3.3 family, C-12).
 */
(function () {
  "use strict";

  var root = document.documentElement;

  function toggle(selector, attr, key, query, onValue, offValue) {
    var button = document.querySelector(selector);
    if (!button) { return; }
    var mq = window.matchMedia(query);

    function current() {
      return root.getAttribute(attr) || (mq.matches ? onValue : offValue);
    }
    function reflect() {
      button.setAttribute("aria-pressed", current() === onValue ? "true" : "false");
    }

    button.hidden = false;
    reflect();
    if (typeof mq.addEventListener === "function") {
      mq.addEventListener("change", reflect);
    }
    button.addEventListener("click", function () {
      var next = current() === onValue ? offValue : onValue;
      root.setAttribute(attr, next);
      try { window.sessionStorage.setItem(key, next); } catch (e) { /* per-page only */ }
      reflect();
    });
  }

  toggle("[data-theme-toggle]", "data-theme", "theme",
         "(prefers-color-scheme: light)", "light", "dark");
  toggle("[data-contrast-toggle]", "data-contrast", "contrast",
         "(prefers-contrast: more)", "more", "normal");
})();
