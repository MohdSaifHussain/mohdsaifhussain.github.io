/* Truth-strip IST clock.  P3.3 / D6.
 *
 * Handoff §3: accent dot + HH:MM:SS IST, 1s tick, Intl with Asia/Kolkata.
 * External file, no inline script (C-18).
 *
 * HONEST DEGRADATION — requirement 3.7.
 * Without JS the server-rendered markup reads "SNAPSHOT <build stamp>", which
 * is true: it is the time the data snapshot was taken. It never shows an empty
 * slot, and it never shows a frozen time dressed up as a live one. Only when
 * this file runs does the label change to a live clock and the live-indicator
 * dot appear — so the dot means "this is ticking", and it means it truthfully.
 *
 * This is not an animation. Text content changing on a timer is not motion:
 * nothing moves, fades or transforms, so it is not on the C-12 list and
 * check_animations.py has nothing to find. The dot does not pulse, for the
 * same reason — a pulsing dot would be a fifth animation nobody declared.
 */
(function () {
  "use strict";

  var host = document.querySelector("[data-clock]");
  if (!host) { return; }
  var text = host.querySelector("[data-clock-text]");
  if (!text) { return; }

  var fmt;
  try {
    fmt = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Asia/Kolkata",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
  } catch (e) {
    /* No Intl, or no tz database: leave the honest snapshot label in place
       rather than substituting the visitor's own clock, which would not be
       IST and would quietly be a false claim. */
    return;
  }

  function tick() {
    text.textContent = fmt.format(new Date()) + " IST";
  }

  tick();
  host.classList.add("is-live");
  setInterval(tick, 1000);
})();
