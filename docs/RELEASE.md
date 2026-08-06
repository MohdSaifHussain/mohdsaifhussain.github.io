# Release protocol

**FULL tier.** The irreversible act is `git tag v1.0.0` and its push. It happens
once, last, only after a release candidate has been verified by hand **and a
negative control has been seen to fail**.

> **Why the negative control is mandatory.** If the verification passes on
> something that should fail, the verification proved nothing — it would have
> passed on anything. A release check that has only ever succeeded is a
> decoration, and this build has already produced two of those and caught them
> only by trying to break them (D-24, D-44).

---

## 1. Pre-flight

Every gate green locally, and every evidence link resolving:

```powershell
python build.py;                   "build exit=$LASTEXITCODE"
python -m pytest;                  "tests exit=$LASTEXITCODE"
python tools\check_c33.py;         "c33 exit=$LASTEXITCODE"
python tools\check_content.py;     "content exit=$LASTEXITCODE"
python tools\check_animations.py;  "animations exit=$LASTEXITCODE"
python tools\check_contrast.py;    "contrast exit=$LASTEXITCODE"
python tools\fetch_stats.py --verify-links;  "links exit=$LASTEXITCODE"
```

## 2. Measure the published site under the protocol

```powershell
gh workflow run measure-live.yml
```

Median of 3 runs per page per profile, both profiles, against the live origin.
**Whatever it returns is what /audit publishes.** No re-run for a better number.

## 3. Cut the release candidate

```powershell
git tag -a v1.0.0-rc.1 -m "Release candidate 1 for v1.0.0"
git push origin v1.0.0-rc.1
```

The RC exercises the **full** publish path. A rehearsal that skips the risky
steps proves only the safe ones.

## 4. Verify the candidate as an outsider would

Fetch the published artefacts fresh — do not inspect the local build:

```powershell
python tools\verify_release.py --tag v1.0.0-rc.1
```

This checks, against the **live** site:

1. every page returns 200 over HTTPS, and `http://` redirects to it;
2. the deployed HTML is **byte-identical** to what this commit builds;
3. the CSP is present and contains no `unsafe-inline`;
4. every evidence link resolves;
5. no contact-capable address or phone number in any served page;
6. /audit publishes measured values with their protocol and environment.

## 5. THE NEGATIVE CONTROL — it must fail

```powershell
python tools\verify_release.py --tag v1.0.0-rc.1 --negative-control
```

Runs the same byte-identity verification against a **deliberately altered**
build. It **must** report `RELEASE VERIFICATION FAILED`. If it passes, step 4
proved nothing and the release stops.

Run it at the final candidate **and again after the real tag**.

## 6. The irreversible act

Only after a fully clean candidate **and the owner's explicit word**:

```powershell
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
python tools\verify_release.py --tag v1.0.0
python tools\verify_release.py --tag v1.0.0 --negative-control
```

**The tag is annotated, not signed.** No signing key is configured for this
repository. "Annotated" is not "signed" and is never described as such — on
/audit or anywhere else.

Deleting a pushed tag does not un-publish it: the commit remains fetchable by
SHA. Treat the push as permanent.

## 7. Failed candidates stay

A candidate that fails is not deleted or quietly replaced. It is the honest
history of the release, and the next candidate is `-rc.2`.
