# SITE CHARTER — mohdsaifhussain.github.io

**Document:** STEP-01 — Design Charter (frozen on owner approval)
**Version:** v1.0 — FROZEN 5 August 2026 on owner sign-off. This text is never edited; all changes are numbered amendments in the Amendment Log.
**Owner:** Mohd Saif Hussain
**Drafted:** 5 August 2026, with Claude (chat) — AI-assisted, honestly declared
**Governs:** the personal portfolio website, hosted on GitHub Pages, built via Claude Design (visual exploration) → Claude Code (governed build)

---

## 1. Purpose & Positioning

The site is itself a portfolio piece: its build quality is the evidence. Every quality claim the site makes about itself must be verifiable, and the site publishes its own audit. The visitor should conclude within ten seconds: *this person builds governed, honest, high-craft systems — and this site is one of them.*

Positioning line (working): a builder of AI-governed systems where the agent proposes, deterministic tools dispose, and every claim is traceable.

## 2. Scope & Non-Goals

**In scope:** static portfolio site; home, projects, experience/resume, certifications & completed courses (badge-style), self-audit page; visible AI-orchestration colophon; privacy-respecting visit counter; a maintenance SOP so the owner can update everything himself; continuous updates as the portfolio grows.

**Deferred — future upgrades, recorded but out of scope for v1:**
- Learning tracker + reminder engine (scheduled Action + GitHub Issue reminders + append-only learning ledger) — designed in discussion 5 Aug 2026, parked to keep v1 simple.
- Runtime AI "/ask" page (browser-side model grounded on site data) — parked; v1 carries no runtime AI.
- Dated build-log ("Now") page — parked; may fold into a future upgrade.

**Non-goals (explicit):**
- No backend, no CMS, no database. Static files only.
- No custom domain at launch (github.io is the home; a domain may be added later without breaking anything).
- No sound or music of any kind.
- No preloader / splash screen.
- No scroll-hijacking or custom smooth-scroll libraries.
- No cookies, no consent banners, no third-party trackers, no PII collection.
- No email address and no phone number anywhere on the site or in its downloadable files. Contact routes exclusively through LinkedIn (GitHub for code).
- No design-award theatrics that cost a single condition below. Where spectacle and legibility conflict, legibility wins. Always.

## 3. Standards Register

Conformance claims are made only where they are testable. Process standards are "informed by," never claimed as certification.

| # | Standard / Framework | Grade adopted | Claim type | Verified by |
|---|---|---|---|---|
| S1 | WCAG 2.2 (W3C) | Level AA full; selected AAA criteria (see C-10, C-14) | Conformance | axe-core, manual audits |
| S2 | WAI-ARIA 1.2 authoring practices | As applicable | Conformance | Manual + axe |
| S3 | WHATWG HTML Living Standard | Valid, semantic | Conformance | W3C Nu validator, zero errors |
| S4 | Core Web Vitals (web.dev) | Stricter-than-"good" budgets | Conformance | Lighthouse, field-tested |
| S5 | CSP Level 3 + W3C Subresource Integrity | Max achievable on static hosting | Conformance within platform limits (§7) | Header/meta inspection |
| S6 | OWASP Secure Headers guidance | Applied where GitHub Pages permits | Informed by | Documented in audit page |
| S7 | GDPR (EU) & DPDP Act 2023 (India) posture | Zero-personal-data design — nothing to comply *about* | Design posture, not legal claim | No cookies, no PII, counter per C-22 |
| S8 | schema.org + Open Graph | Person + CreativeWork markup | Conformance | Rich-results/validator check |
| S9 | ISO 9241-210 human-centred design; owner's own governed-build method | Process | Informed by | Decision docs, defect log |

## 4. Conditions

Each condition is binary at phase close: MET / UNMET, with evidence. Verification method in brackets.

### A. Performance
- **C-01** Lighthouse 100/100/100/100 (Performance, Accessibility, Best Practices, SEO) on every page, mobile and desktop profiles. [Lighthouse CI]
- **C-02** LCP ≤ 1.5 s on simulated mid-tier mobile; CLS = 0.00; INP ≤ 200 ms. [Lighthouse / DevTools]
- **C-03** Total transfer for first view of the home page ≤ 500 KB, including fonts and images. [DevTools network]
- **C-04** Zero render-blocking third-party resources. Fonts self-hosted, `font-display: swap` or better. [Audit]
- **C-05** Images in modern formats (AVIF/WebP with fallback), explicitly sized (no layout shift), lazy-loaded below the fold. [Audit]

### B. Accessibility (WCAG 2.2 AA + selected AAA)
- **C-06** Zero axe-core violations on every page. [axe DevTools / CI]
- **C-07** Full keyboard pass: every interactive element reachable, operable, and escapable by keyboard alone; visible focus states everywhere; logical tab order; skip-to-content link. [Manual pass, scripted where possible]
- **C-08** Screen-reader smoke test with NVDA on Windows: all content and navigation comprehensible; all images carry meaningful alt text or are marked decorative. [Manual, findings logged]
- **C-09** Color contrast ≥ 4.5:1 for body text (AA); ≥ 7:1 wherever the monochrome palette permits (AAA 1.4.6, adopted as target, not claim). [Contrast checker]
- **C-10** AAA 2.3.3 Animation from Interactions adopted as a hard rule: all non-essential motion disabled under `prefers-reduced-motion: reduce`. The site must remain fully coherent and complete with motion off. [Manual toggle test]
- **C-11** `lang` attributes correct; text resizable to 200% without loss of content or function; no information conveyed by color alone. [Manual]

### C. Motion & Interaction (the anti-lost doctrine)
- **C-12** Every animation answers exactly one of: *where am I* / *what just happened* / *what can I do*. Any animation answering none is a defect. Each shipped animation is listed in the audit page with its declared purpose. [Design review at phase close]
- **C-13** Navigation persistently visible or one interaction away at all times; current location always indicated; any page reachable within two interactions from anywhere. [Manual]
- **C-14** Native scrolling only. Scroll-driven effects may respond to scroll position but never alter scroll physics. Sliders/carousels use CSS scroll-snap, are keyboard- and swipe-operable, and show position (e.g., 01 / 07). [Manual]
- **C-15** Micro-interactions 150–250 ms; transitions ≤ 400 ms; animate `transform` and `opacity` only (compositor-friendly); no `width`/`height`/`top`/`left` animation; sustained 60 fps on mid-tier hardware. [DevTools performance trace]
- **C-16** Every interactive element gives feedback within 100 ms of input. [Manual]

### D. Security & Privacy
- **C-17** HTTPS enforced (GitHub Pages "Enforce HTTPS" on). [Settings + probe]
- **C-18** Content-Security-Policy via `<meta http-equiv>`: no inline scripts, no `eval`, explicit allowlist covering only self and the analytics endpoint. [Meta inspection + violation-free console]
- **C-19** Subresource Integrity on any resource not served from the repo; target state: zero third-party resources except the counter. [Audit]
- **C-20** `<meta name="referrer" content="no-referrer">` (or stricter policy justified in audit). All external links `rel="noopener noreferrer"`. [Audit]
- **C-21** No cookies set by the site. No localStorage of personal data. No fingerprinting. [DevTools application tab]
- **C-22** Visit counter: GoatCounter (or equivalent meeting all of: free tier, no cookies, no PII, script ≤ 5 KB, degrades silently if blocked). Count may be displayed publicly. [Audit]

### E. Markup, Metadata & SEO
- **C-23** Zero errors on the W3C Nu HTML validator, every page. [Validator]
- **C-24** Semantic landmarks (`header/nav/main/footer`), one `h1` per page, heading levels never skipped. [Audit]
- **C-25** Complete metadata: title/description per page, Open Graph + Twitter card with a real OG image, canonical URLs, `sitemap.xml`, `robots.txt`, favicon set + web manifest. [Audit]
- **C-26** JSON-LD structured data: `Person` on home; `SoftwareSourceCode`/`CreativeWork` per project. Validates clean. [Rich-results test]

### F. Content Honesty (standing resume rules apply)
- **C-27** Every metric shown on the site (test counts, defect counts, scores) traces to a verifiable source — a repo, a report, or the site's own audit. No inflated claims. No em-dashes in resume-derived text. [Owner review]
- **C-28** AI collaboration honestly framed, consistent with existing project documentation: built by Saif directing Claude. [Owner review]
- **C-29** The downloadable resume PDF and on-site experience content never contradict each other. [Owner review at every update]

### G. Governance & Self-Audit
- **C-30** The site ships a public **/audit** page: current Lighthouse scores, axe result, validator result, the standards register (§3), the platform constraint register (§7), the shipped-animations list (C-12), and the build's defect log summary. Regenerated at every release. [Presence + freshness check]
- **C-31** Build follows the governed method: this charter frozen before visual work; phased build in Claude Code; conditions checked at each phase close; defects logged with honest classification; charter amendments (if any) logged with reason, never silently edited. [Decision docs in repo]
- **C-32** The repo is public and includes decision docs, so the build process is itself inspectable evidence. [Repo review]

### H. Content & Data Architecture
- **C-33** No email address or phone number appears anywhere: not in visible content, markup, metadata, structured data, alt text, commit-published files, or the downloadable web resume PDF. Contact points to LinkedIn only (plus GitHub for code). [Repo-wide grep + PDF review at every release]
- **C-34** Single source of truth: all portfolio content (identity, projects, experience, certifications, build log) lives in structured data files (JSON/YAML) in the repo; every page is generated from that data at build time; no content hand-duplicated across pages. Updating the site = editing data + push. [Repo review]
- **C-35** GitHub-derived stats (repos, releases, test counts) are fetched at build time — never client-side — snapshotted with a visible "as of" timestamp, and sourced per C-27. [Build script review + /audit]
- **C-36** The repo ships `docs/SOP.md` — the owner's maintenance manual, written for his actual environment (Windows, PowerShell-safe commands): step-by-step procedures for (a) adding a new project, (b) adding a certification/completed course, (c) editing profile or experience data, (d) replacing the web-resume PDF, (e) the pre-release checklist (run Lighthouse, axe, validator; confirm conditions; refresh /audit), and (f) filing a charter amendment. Every procedure is tested once by actually performing it before release. [SOP walkthrough at release]

## 5. Design Direction

- **Palette:** monochrome (near-black / off-white) plus exactly one accent color. Dark-first; light mode optional later, never at the cost of C-09.
- **Typography:** two typefaces maximum, self-hosted. Extreme scale contrast — large display headings, small dense metadata text, minimal middle register.
- **Motif:** one repeated mark used relentlessly — nominated: the verification mark (✓ / ✗) and/or a ledger rule line, echoing the audit-report language of the owner's own tools. (Chosen and locked during Claude Design exploration; recorded as an amendment note, not a charter change.)
- **Numbered structure:** sections and project sliders numbered (01 / 07 style) — orientation as aesthetic.
- **Ambient truth details:** live IST clock, Hyderabad location stamp, live-true stats (tests passing, defects logged, refusals to overclaim). Every ambient detail must be true and sourced (C-27).
- **Identity mark:** no logo. The mark is a typographic wordmark — **MOHD SAIF HUSSAIN** set in the display face — in the nav and footer. A photo of the owner may appear in the home introduction (decided at Design phase); the wordmark, not the photo, is the site's mark.
- **Certification badges:** LinkedIn-style badge tiles rendered from `certifications.json` — issuer, course, completion date, link to official credential verification. Tiles are typographic, in the site's own design language; **no third-party issuer logos or trademarks** are reproduced (IP discipline + zero external assets). Visual treatment of the tiles: Claude Design's creative freedom within §5.
- **Colophon:** every page footer carries one professional line — *"An AI-orchestrated portfolio: designed and built by Mohd Saif Hussain directing Claude, under a governed, audited process."* — linking to /audit for the full method. This satisfies C-28 visibly.
- **Voice:** ledger, not sci-fi. Receipts, not manifesto.
- **Reference:** daoism.systems studied for type scale, motif discipline, hover disclosure, and restraint — not replicated; its preloader, sound, and disorientation explicitly rejected (§2, C-12–C-14).

## 6. Site Architecture

1. **Home** — identity line, flagship projects (proof-first), ambient truth strip, wordmark nav.
2. **Projects** — full set as case studies; per-project: problem, method, verified metrics, defects/refusals, links (repo, GHCR, report).
3. **Experience** — work history; web-resume PDF download (contact-stripped per C-33).
4. **Certifications & Courses** — badge-tile grid from `certifications.json`; each tile links to official verification.
5. **/audit** — the site's own report card (C-30), including the colophon's full story.

Footer on every page: wordmark, LinkedIn + GitHub links, colophon line, visit count.

## 6A. Content Architecture (how information enters the site)

**Sources of truth:** the owner's resume and GitHub profile. Nothing else generates content.

**Pipeline:**
1. Resume + GitHub profile are parsed once into structured data files (`data/profile.json`, `data/projects.json`, `data/experience.json`, `data/certifications.json`), field-by-field verified by the owner (C-27).
2. A small deterministic build script (Python + templates) renders the data files into static HTML. Presentation and content never mix by hand.
3. GitHub Actions runs the build on every push (and on a schedule for C-35 stats refresh) and publishes to Pages.
4. **Updating the site thereafter = editing one data file and pushing.** New project → add an entry to `projects.json`. New certification or completed course → one entry in `certifications.json`. No HTML is ever edited to update content. Exact procedures live in the SOP (C-36).

**Resume handling:** the site offers a **web version** of the resume PDF with email/phone stripped and LinkedIn as the contact line (C-33). The full-contact resume remains private, used only in direct applications. The web PDF and on-site experience data must never contradict (C-29).

**Contact:** LinkedIn profile link only, plus GitHub profile link. No contact form, no mailto.

**Design dependency:** Claude Design works from the real content inventory — actual project names, actual metrics, actual line lengths — never lorem ipsum. Content is inventoried before visual exploration begins (§8 Phase 1).

## 7. Platform Constraint Register (GitHub Pages — honest limits)

| Constraint | Consequence | Mitigation |
|---|---|---|
| No custom HTTP response headers | Cannot set HSTS preload, X-Frame-Options, full server-side CSP | CSP via meta (C-18); HTTPS enforced by platform; limits declared on /audit — never claimed as met when they aren't |
| Static hosting only | No server-side counter, forms, or auth | Counter via GoatCounter (C-22); contact = LinkedIn only (owner decision, C-33) |
| Public repo required (free tier) | Source fully visible | Treated as a feature (C-32) |

Claims beyond this register (e.g., "highest-grade security") are prohibited as inflation. The claim is: *maximum achievable on this platform, with the gap documented.*

## 8. Build Governance

- **Phase 0 (chat):** this charter — frozen on approval.
- **Phase 1 (chat/Claude Code):** content inventory — resume + GitHub parsed into the data files of §6A, every field owner-verified, web-resume PDF prepared with contact stripped. Output: the real content the design will be built around.
- **Phase 2 (Claude Design):** visual exploration against §5, using the Phase 1 content — real names, real numbers, real text lengths. Output: chosen direction + handoff bundle. Design may not add anything banned in §2 or violating §4.
- **Phase 3+ (Claude Code):** governed build in phases (build script + skeleton → content wiring → motion → hardening → audit page), each phase closed against its conditions, defects logged. Phase-close commands written for the actual shell in use (PowerShell-safe).
- **Release rule:** no release with an UNMET condition unless it is declared on /audit as a known limitation with reason.
- **Amendment rule:** post-freeze changes to this charter are appended as numbered amendments with date and reason. The original text is never edited.

---

## Amendment Log

*(Amendments are appended here, numbered, dated, with reason. The charter text above is never edited.)*

### Amendment 1 — C-33 scoped to contact-capable addresses

**Date:** 2026-08-06
**Filed by:** Mohd Saif Hussain (owner/director), during P3.1, before the first commit existed
**Amends:** C-33 (§4, H. Content & Data Architecture)
**Status:** Adopted

**Amendment text.** C-33's prohibition is scoped to **contact-capable** email addresses. Addresses at `users.noreply.github.com`, which cannot receive mail, are exempt in two places and two only: (a) git commit author/committer metadata, and (b) documentation recording the git configuration command. Every other provision of C-33 stands unchanged — no contact-capable address and no phone number appears in visible content, markup, metadata, structured data, alt text, commit-published files, or the downloadable web resume PDF. Contact continues to route exclusively through LinkedIn, plus GitHub for code.

**Reason.** Git authorship structurally requires an email address; a commit cannot be authored without one. Discovered before the first commit during P3.1, logged as defect D-10, while no history yet existed to correct.

**Why amended rather than allowlisted in the checker alone.** The frozen text and the reported verdict must agree. An exception recorded only on /audit would leave the charter permanently contradicting its own MET claim — the site would assert a condition its own governing document forbids it to meet.

**Verification.** `tools/check_c33.py` implements this as a deterministic allowlist of `@users.noreply.github.com` and nothing else:
- **negative control:** a poisoned fixture containing a routable-looking address must still trip the check (non-zero exit);
- **positive control:** a fixture of ISO-8601 dates must not trip it (defect D-11);
- /audit's C-33 row cites this amendment by number.

*Superseded in precision by Amendment 2, which states C-33's purpose explicitly and replaces the single exemption with an enumerated list. Amendment 1's exemption stands unchanged as item (1) of that list.*

### Amendment 2 — C-33 exemptions enumerated, not pattern-matched

**Date:** 2026-08-06
**Filed by:** Mohd Saif Hussain (owner/director), during P3.1, before the first commit
**Amends:** C-33 (§4, H), extending Amendment 1
**Status:** Adopted

**Purpose clause.** C-33 exists so that contact with the owner routes exclusively through LinkedIn. Addresses that are **not contact routes to the owner** and are structurally or conventionally non-routing are exempt in commit metadata and attribution trailers.

**Exemptions are enumerated, not pattern-matched:**

1. `*@users.noreply.github.com` — required for git authorship (Amendment 1).
2. The literal `noreply@anthropic.com`, **solely** as the `Co-Authored-By` AI-attribution trailer, which serves C-28 by recording the AI collaboration in the commit record itself.

Any future attribution address requires its own recorded allowlist decision. No address is exempt by resembling an exempt one.

**Everything else in C-33 stands:** no contact-capable address and no phone number in visible content, markup, metadata, structured data, alt text, commit-published files, or the web resume PDF.

**Verification.** `tools/check_c33.py` implements the list by enumeration, with two negative controls:
- a routable-looking address must trip the check;
- **`noreply@` at any unlisted domain must also trip it** — which is what proves the implementation enumerates rather than pattern-matches. A pattern-based check would pass this case and look identical to a correct one.

Defect D-17. /audit's C-33 row cites Amendments 1 and 2.

---

*v1.0 — FROZEN 5 August 2026 on owner sign-off. Copied verbatim into the site repo as `docs/decisions/STEP-01-CHARTER.md` at Phase 3 start.*
