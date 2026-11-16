# Y-Lab Website (`Y-Lab-Website`) Agent Guidelines

## Git & Version Control
- **Do NOT commit or push:** Never execute `git commit` or `git push` under any circumstances.
- **Leave changes for user review:** Make all edits directly in the working tree and leave them unstaged/uncommitted so the user can inspect diffs and perform git operations manually.
- **No Git tutorials:** Never include step-by-step basic Git instructions (`git add`, `git commit`, `git push`, etc.).

## Documentation & Issue Style
- **Uncluttered & Academic:** Keep documentation and GitHub issues concise, readable, and professional.
- **No Decorative Emojis:** Avoid emojis in issue titles, headers, bullet points, and tables.
- **Explicit AI-Drafted Notice on Generated Issues:** Any GitHub issue drafted for the PI or lab review must begin with a clear note stating it was drafted by an AI assistant, so Dr. Yan knows it was not written directly by a lab member.
- **Direct GitHub File Links:** When referencing repository files in GitHub issues, link directly to `https://github.com/Y-Lab-UC-Davis/Y-Lab-Website/blob/main/<path>` (with `#L<start>-L<end>` when relevant), and include `edit/main/<path>` links on PI-review issues.
- **Approve / Modify / Disapprove Format for PI Issues:** Do not use multiple-choice checkboxes (`- [ ] Option A / Option B`) on `pi-input` issues. State what is needed, present a single proposed default/draft, and ask Dr. Yan to reply with **Approve**, **Modify**, or **Disapprove**. Split multi-topic requests into small, single-topic issues.

## GitHub Operations (`gh` & Workflows)
- **Never add `website-update` to task or photo issues:** `.github/workflows/issue-to-pr.yml` triggers `scripts/issue_to_change.py` on any open issue carrying the `website-update` label. Only the three automated content forms in `.github/ISSUE_TEMPLATE/` (`add-news.yml`, `add-conference-paper.yml`, `add-press.yml`) should use `website-update`. Photo submissions (`add-photo.yml`) use the `photo` label and are handled manually by maintainers.
- **Check existing issues and labels first:** Verify existing items with `gh issue list` and `gh label list` before creating new issues or referencing labels.

## YAML Data Files & Python Sync Scripts
- **Preserve example blocks and comments:** Always keep `EXAMPLE ENTRY` / `EXAMPLE STRUCTURE` / `MEMBER TEMPLATE EXAMPLE` comments and field documentation intact in `_data/*.yml`. Scripts that rewrite `_data/*.yml` (`scripts/sync_people.py`, `scripts/update_publications.py`) must preserve these headers, examples, and section comments.
- **Initialize empty YAML lists as `[]`:** Never leave empty list keys blank (`null`); Liquid `concat` filters fail on `nil`.
- **Single source of truth for member profiles:** Member registration and bio/link updates belong in `lab-admin` (`member-registration.yml` -> `members/*.yml`), synced into `_data/people.yml` via `scripts/sync_people.py` (which preserves manual `photo`, `awards`, `aliases`, `last`, `orcid`, and `role_icon` fields). Do not re-enable `add-person.yml` on the website; collect headshots separately via `add-photo.yml`.
- **Public privacy boundaries (`scripts/sync_people.py`):** When syncing profiles from `../lab-admin/members/*.yml` into `_data/people.yml`, never copy `email_personal`, `desk_location`, `bainer_access`, or `lab_access`, and omit personal contact links (`email`, `linkedin`, `orcid`, `scholar`, `website`, `github`) for undergraduate and visiting researcher entries.
- **Publications sync (`scripts/update_publications.py`):** Syncs by Dr. Yan's ORCID (`0000-0002-3711-0807`) via OpenAlex. Never remove manual entries or exclusions; unwanted DOIs returned by OpenAlex belong under `exclude:` in `_data/publications_manual.yml`.

## Liquid Templates & Verification
- **Guard optional data and assets:** Wrap optional sections (`recognition.awards`, `recognition.media`, `funders`, `collaborators`, `press`, `alumni`, `assets.hero_video`, `assets.lab_photo`) and conditional anchors (`#blog`, `#in-the-news`) in Liquid existence checks so empty YAML files never render broken links or fail `htmlproofer`.
- **Validate locally after edits:** Parse all `.yml` files with `yaml.safe_load`, `py_compile` modified Python scripts, and run `python3 scripts/optimize_images.py --check`.
