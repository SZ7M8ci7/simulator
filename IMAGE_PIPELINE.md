# Card image pipeline

`get_img.py` validates every existing source image and downloads all missing or corrupt sources sequentially. A source must pass content checks and Pillow verify/load before an atomic replacement. HTML challenges are errors, never cached images. Valid existing sources are skipped. No authentication challenge is solved or bypassed.

Requests use 10/30 second connect/read timeouts, a one-second minimum interval, up to three attempts for temporary failures, and exponential backoff. 404/403 do not retry immediately and do not block later cards. Retry-After is respected; a delay over 30 seconds defers remaining requests to a later scheduled run.

`make_icon.py` checks sources and both outputs, continues after individual failures, and writes PNG/WebP only after both renders validate. It uses card keys directly instead of reverse-mapping filenames. Repaired/downloaded source cards refresh their generated icons; other valid outputs are left untouched.

Run from the repository root with Python 3.10 and requirements.txt installed:

```sh
python -m unittest discover -s tests -v
python get_img.py
python make_icon.py
```

Both commands return exit code 1 when any card remains unresolved. Reports in `reports/get-images.json` and `reports/make-icons.json` identify every card, status and error. Download reports also include the source URL and attempt count. Reports are ignored by Git, retained as Actions artifacts for 30 days, and failures are listed in the job summary. A valid partial update is committed even if other cards failed; the final workflow result still fails visibly. The get/make schedules share a concurrency group, and image commits rebase before pushing to avoid overwriting concurrent data updates.

## Reviewed source filenames

`image_sources.json` contains exact attachment names, not replacement artwork. The two Grim source files use uppercase `.JPG`. Four basic Ortho cards still use the old attachment labels 制服, 運動着, 式典服 and 実験着. The checked-in costume dictionary maps these labels to the same card keys as アーキタイプ・ギア, アスレチック・ギア, バースト・ギア and プレシジョン・ギア; a regression test verifies that identity. Downloads are stored under the canonical current filename. Existing source URLs were verified to return decodable images on 2026-10-08.

## 2026-10-08 repair result

All 528 catalog cards were checked. Eleven invalid cached sources were repaired, three newly available sources were downloaded, and PNG/WebP were generated from the verified sources. Published icon gaps can be reduced from ten to one after syncing these changes: `jack_great_look` remains unavailable at the source URL (404), and its card page has no card artwork. No substitute was generated. It remains explicit in the reports and causes a nonzero job result until a verified source becomes available.

Nothing in this repair branch has been pushed or deployed. Local test result: 26 pipeline regression tests passed. The corresponding isolated twst checkout checks all display icons after synchronization and after the recognition catalog merge; 527/528 are valid, with only Jack unresolved.
