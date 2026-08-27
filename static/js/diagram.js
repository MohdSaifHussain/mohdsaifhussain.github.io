/* A3.7 — the architecture diagrams on /projects/.  v1.2 / P5.4.
 *
 * POSTING. Arms every .diagram that sits ENTIRELY below the viewport when
 * this runs, then posts each one the first time it reaches the reading edge.
 * A diagram already on screen, every diagram without JS, and every diagram
 * for a visitor who asked for reduced motion is never touched: visible from
 * the first frame. Posting happens once; the observer lets go of it after.
 *
 * ZOOM. Each figure's buttons scale the drawing inside its own scrollable
 * frame by setting the SVG's width. The controls are reserved in the layout
 * and revealed here (visibility), so nothing shifts when they appear.
 *
 * No scroll listener, no wheel listener, nothing that drives or suppresses
 * scrolling (C-14). External file, no inline script (C-18). No library (C-19).
 */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- posting ---------------------------------------------------------- */
  if ("IntersectionObserver" in window && !reduced) {
    var vh = window.innerHeight;
    var armed = [];
    Array.prototype.forEach.call(document.querySelectorAll(".diagram"), function (d) {
      if (d.getBoundingClientRect().top >= vh) {
        d.classList.add("post-pending");
        armed.push(d);
      }
    });
    if (armed.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) { return; }
          var d = entry.target;
          d.classList.add("is-posted");
          window.setTimeout(function () {
            d.classList.remove("post-pending", "is-posted");
          }, 3000);
          observer.unobserve(d);
        });
      }, { rootMargin: "0px 0px -10% 0px", threshold: 0.15 });
      armed.forEach(function (d) { observer.observe(d); });
    }
  }

  /* ---- zoom -------------------------------------------------------------- */
  var STEPS = [1, 1.5, 2, 2.5, 3];
  Array.prototype.forEach.call(document.querySelectorAll(".diagram-wrap"), function (wrap) {
    var svg = wrap.querySelector(".diagram");
    var controls = wrap.querySelector(".diagram-zoom");
    if (!svg || !controls) { return; }
    var level = 0;
    function apply() {
      svg.style.width = (STEPS[level] * 100) + "%";
      controls.querySelector('[data-zoom="out"]').disabled = level === 0;
      controls.querySelector('[data-zoom="in"]').disabled = level === STEPS.length - 1;
    }
    controls.addEventListener("click", function (e) {
      var b = e.target.closest("[data-zoom]");
      if (!b) { return; }
      if (b.dataset.zoom === "in" && level < STEPS.length - 1) { level += 1; }
      if (b.dataset.zoom === "out" && level > 0) { level -= 1; }
      if (b.dataset.zoom === "reset") { level = 0; }
      apply();
    });
    apply();
    controls.classList.add("is-live");
  });
})();
