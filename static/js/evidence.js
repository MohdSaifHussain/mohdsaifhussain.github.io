/* A3.1 — Home flagship row evidence reveal.  P3.3 / D1.
 *
 * Handoff §4 and §5. Opacity only, 200ms, driven by ROW-LEVEL state in JS
 * rather than a descendant CSS selector.
 *
 * Why row-level JS and not :hover on the row: the committed design was rebuilt
 * specifically because an earlier version covered the links column. A CSS
 * descendant hover would re-open that risk the moment the layer's bounds
 * changed. Here the layer's bounds are fixed in CSS, the layer is
 * pointer-events:none, and this file only ever toggles one class.
 *
 * The layer spans the name + problem columns ONLY. The links column is never
 * covered in any state — requirement 3.3, re-proved at the review stop rather
 * than assumed from the design.
 *
 * External file, no inline script: C-18.
 * Reduced motion is handled entirely in CSS via --motion-reveal, so this file
 * needs no knowledge of it and cannot disagree with it.
 */
(function () {
  "use strict";

  var rows = document.querySelectorAll("[data-evidence-row]");

  Array.prototype.forEach.call(rows, function (row) {
    function show() { row.classList.add("is-revealed"); }
    function hide() { row.classList.remove("is-revealed"); }

    row.addEventListener("mouseenter", show);
    row.addEventListener("mouseleave", hide);

    /* Keyboard parity: the row reveals when any control inside it takes focus,
     * so a keyboard user reaching REPO or CONTAINER sees the same evidence a
     * pointer user sees. No tabindex is added to the row itself — that would
     * create a tab stop with no action (C-07, C-08). */
    row.addEventListener("focusin", show);
    row.addEventListener("focusout", function (e) {
      if (!row.contains(e.relatedTarget)) { hide(); }
    });
  });
})();
