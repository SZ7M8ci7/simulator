# Card image pipeline

## Expected absence versus actual errors

The pipeline distinguishes `pending` from `error`:

| Situation | Result | Exit / notification |
| --- | --- | --- |
| Exact source URL returns HTTP 404 and no corrupt cache exists | pending; retry next scheduled run | 0; no warning/error or notification summary |
| Source file does not exist yet; no malformed output exists | pending | 0; no warning/error or notification summary |
| HTML, empty/truncated image, invalid format/dimensions | error unless successfully repaired | nonzero; actual error in summary/report |
| HTTP 401/403, exhausted 429/5xx/timeout retries, processing/permission failure | error | nonzero; actual error in summary/report |
| Corrupt existing source cannot be repaired because its URL now returns 404 | error (corruption remains) | nonzero; never downgraded to pending |

Pending card details are retained only in diagnostic JSON (`pendingCount` and per-card `status: pending`); they are not listed in the job summary. An ordinary missing-file message is not emitted. Mixed runs report only actual errors. `failedCount` counts errors, not pending cards.

`get_img.py` checks every existing source with Pillow verify/load and validates response contents before an atomic replacement. HTML challenges are never saved as images. Valid sources are skipped; missing or corrupt sources are processed sequentially without stopping later cards. No challenge is solved or bypassed.

Requests have connect/read timeouts, at least one second between requests, three bounded attempts for temporary failures and exponential backoff. 404/403 do not retry immediately. Retry-After is respected; a wait over 30 seconds defers later network requests as a reported rate-limit error rather than ignoring the server limit.

`make_icon.py` verifies source/output content and renders both formats before replacing either file. Missing source files are pending, but malformed existing outputs, missing render dependencies and actual errors from the download report remain errors. Repaired/downloaded sources refresh their icons; other valid outputs are untouched.

```sh
python -m unittest discover -s tests -v
python get_img.py
python make_icon.py
```

Reports are written to `reports/get-images.json` and `reports/make-icons.json`, ignored by Git and retained as Actions artifacts for 30 days. Only actual errors create a job summary and trigger the final workflow failure. Verified partial assets are still committed before that final failure step. Get/make workflows share a concurrency group.

`image_sources.json` holds reviewed attachment filenames for two uppercase-JPG Grim sources and four legacy Ortho costume names. Regression tests check that these resolve to the same card identity; no substitute artwork is generated.

## Pending-policy validation (2026-10-08)

34 pipeline regression tests pass, including pending-only success without a summary, HTML/decode failure, authentication/rate/transport errors, mixed pending/error/success, corrupt cache plus 404, and later image availability. All 528 real catalog entries were checked locally: 527 available, `jack_great_look` pending, zero errors. Both acquisition and generation exit 0 without an error/warning notification. This policy was validated locally before publication; the policy adjustment does not change image assets.
