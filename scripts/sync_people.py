#!/usr/bin/env python3
"""
sync_people.py: populate _data/people.yml from member profiles in ../lab-admin/members/.

Safe by design:
  * Preserves the `pi`, `affiliates`, and `alumni` sections in _data/people.yml.
  * Preserves manual website-only fields (`photo`, `awards`, `aliases`, `last`,
    `orcid`, `role_icon`) on any matched member already in _data/people.yml.
  * Preserves the full documentation header, example template, and section comments.
  * Never exports private logistics (`email_personal`, `desk_location`, building/lab
    access booleans) and omits contact links for undergraduate entries per the site's
    privacy convention.

Run locally:  python3 scripts/sync_people.py
              python3 scripts/sync_people.py --members-dir ../lab-admin/members
"""
from __future__ import annotations

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MEMBERS_DIR = os.path.abspath(os.path.join(REPO_ROOT, "..", "lab-admin", "members"))
PEOPLE_YML = os.path.join(REPO_ROOT, "_data", "people.yml")

ROLE_MAP = {
    "postdoc": ("postdoc", "Postdoctoral Scholar"),
    "phd_candidate": ("phd", "PhD Candidate"),
    "phd": ("phd", "PhD Student"),
    "msc": ("msc", "MSc Student"),
    "undergrad": ("undergrad", "Undergraduate Researcher"),
    "visiting_undergrad": ("undergrad", "Visiting Undergraduate Researcher"),
    "visitor": ("visiting", "Visiting Researcher"),
    "staff": ("visiting", "Lab Staff / Affiliate"),
}

GROUP_META = [
    ("pi", "Principal Investigator"),
    ("postdoc", "Postdoctoral Scholars"),
    ("phd", "PhD Researchers"),
    ("msc", "Master's Students"),
    ("undergrad", "Undergraduate Researchers"),
    ("visiting", "Visiting Researchers"),
]

NO_CONTACT_GROUPS = {"undergrad", "visiting"}
PRESERVED_MANUAL_KEYS = ("photo", "awards", "aliases", "last", "orcid", "role_icon")
MEMBER_FIELD_ORDER = (
    "name", "aliases", "role", "role_icon", "pronouns", "field", "last",
    "start", "photo", "email", "website", "scholar", "orcid", "linkedin",
    "github", "note", "awards", "now",
)

HEADER = """\
# ─────────────────────────────────────────────────────────────
#  PEOPLE
#  Groups defined below drive the /people/ directory page.
#  Supported Group IDs: pi, postdoc, phd, msc, undergrad, visiting, affiliates, alumni.
#
#  Member entries under postdoc / phd / msc / undergrad / visiting can be
#  synced from ../lab-admin/members/*.yml via:
#      python3 scripts/sync_people.py
#  Manual website-only fields (`photo`, `awards`, `aliases`, `last`, `orcid`)
#  are preserved across sync runs.
#
#  PHOTO (optional). Two ways, both end with a file in assets/img/people/:
#    • Easiest: drop an already-small square JPG straight into
#      assets/img/people/  (e.g. assets/img/people/jane-doe.jpg).
#    • Or: drop a large original in assets/img/people/_raw/ and run
#      `bash scripts/apply-images.sh` to auto-crop/optimize it into the folder.
#    Then add:  photo: /assets/img/people/jane-doe.jpg
#    No photo = a clean initials avatar.
#
#  ROLE BADGE is inferred automatically from each person's `role` text.
#  Override one with  role_icon: "..."  if needed.
#
#  FIELD (optional), shows small discipline tag(s) so the lab's multidisciplinary
#  mix is visible. Comma-separate for more than one, e.g.
#    field: "Mechanical Engineering, Robotics"
#
#  SORTING: the team grid lists each role by LAST NAME A–Z. The last name is the
#  last word of `name` by default. If that guess is wrong for someone (e.g. a
#  two-word surname with no hyphen), add a `last:` line with the surname to
#  sort by, e.g.  last: "van Dijk".
#
#  MEMBER TEMPLATE EXAMPLE:
#
#  groups:
#    - id: pi
#      title: Principal Investigator
#      members:
#        - name: Dr. Jane Doe
#          aliases: ["Jane Doe"]
#          role: Assistant Professor · Lab Director
#          pronouns: she/her
#          field: "Mechanical Engineering"
#          start: 2026
#          photo: /assets/img/people/jane-doe.jpg # Optional, place in assets/img/people/
#          email: jdoe@university.edu
#          website: https://example.com
#          scholar: https://scholar.google.com
#          orcid: 0000-0000-0000-0000
#          linkedin: https://www.linkedin.com/in/janedoe
#          github: https://github.com/janedoe
#          note: Brief description or research focus.
#          awards:
#            - "NSF CAREER Award"
#
#    - id: phd
#      title: PhD Researchers
#      members:
#        - name: Alex Smith
#          role: PhD Student
#          pronouns: they/them
#          field: "Aerospace Engineering"
#          start: 2026
#          email: asmith@university.edu
#
#  alumni:
#    title: Alumni
#    members:
#        - { name: Alex Smith, role: "Undergraduate Researcher", start: 2024, now: "Stanford University" }
#
# ─────────────────────────────────────────────────────────────
"""

GROUP_COMMENTS = {
    "msc": [
        "  # Master's students. Kept here (empty) on purpose so a submitted \"MSc Student\"",
        "  # auto-files into it. While empty it shows nothing on the site; members appear",
        "  # as soon as one is added. Keep `members: []` (an empty list) while empty so",
        "  # the site build stays happy; the automation swaps it for a real list when it",
        "  # adds the first person.",
    ],
    "visiting": [
        "  # Visiting researchers (non-undergraduate). Kept here (empty) on purpose so a",
        "  # submitted \"Visiting Researcher\" auto-files into it. While empty it shows",
        "  # nothing; members appear once added. Keep `members: []` while empty.",
    ],
}

AFFILIATES_COMMENT = [
    "# Individual collaborators and affiliated researchers outside the core group.",
    "# (Partner *organizations* live in collaborators.yml and appear on the home page.)",
]

ALUMNI_COMMENT = [
    "# Past members.",
    "#  TO RETIRE SOMEONE: cut their whole block from `groups` above (from its",
    "#  `- name:` line through its last field) and paste it below AS IS: the",
    "#  indentation here matches the groups, so no re-indenting is needed. Then just",
    "#  add a `now:` line (current position / destination); until you do, the table",
    "#  shows a dash. `start` (year joined) and `linkedin` carry over automatically.",
    "#  `role` = position held in the lab; `now` = current position / destination.",
]


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def extract_year(date_str: str | int | None, default: int = 2025) -> int:
    m = re.search(r"\b(19|20)\d{2}\b", str(date_str or ""))
    return int(m.group()) if m else default


def load_admin_members(members_dir: str) -> list[dict]:
    if not os.path.isdir(members_dir):
        sys.exit(f"ERROR: members directory not found: {members_dir}")
    members = []
    for name in sorted(os.listdir(members_dir)):
        if name.startswith("_") or not name.endswith(".yml"):
            continue
        data = load_yaml(os.path.join(members_dir, name))
        if isinstance(data, dict) and data.get("full_name"):
            members.append(data)
    return members


def index_existing(people_data: dict) -> dict[str, dict]:
    by_name = {}
    for g in people_data.get("groups") or []:
        if g.get("id") == "pi":
            continue
        for m in g.get("members") or []:
            if isinstance(m, dict) and m.get("name"):
                by_name[m["name"].strip().lower()] = m
    return by_name


def build_member_entry(src: dict, existing: dict | None) -> tuple[str, dict]:
    raw_role = str(src.get("role") or "undergrad").strip().lower()
    gid, role_title = ROLE_MAP.get(raw_role, ("undergrad", "Undergraduate Researcher"))
    home_inst = str(src.get("home_institution") or "").strip()
    if home_inst and raw_role in ("visitor", "visiting_undergrad"):
        role_title = f"{role_title} · {home_inst}"
    full_name = str(src.get("full_name") or "").strip()

    entry: dict = {
        "name": full_name,
        "role": role_title,
        "start": extract_year(src.get("date_joined"), default=2025),
    }

    pronouns = str(src.get("pronouns") or "").strip().lower()
    if pronouns:
        entry["pronouns"] = pronouns

    major = str(src.get("major") or "").strip()
    if major:
        entry["field"] = major

    pub = src.get("public_profile") or {}
    if not isinstance(pub, dict):
        pub = {}

    if gid not in NO_CONTACT_GROUPS:
        email = str(src.get("email_ucdavis") or "").strip()
        if email:
            entry["email"] = email
        website = str(pub.get("personal_website") or "").strip()
        if website:
            entry["website"] = website
        scholar = str(pub.get("google_scholar") or "").strip()
        if scholar:
            entry["scholar"] = scholar
        orcid_raw = str(pub.get("orcid") or "").strip()
        if orcid_raw:
            m = re.search(r"\d{4}-\d{4}-\d{4}-[\dxX]{4}", orcid_raw)
            entry["orcid"] = m.group() if m else orcid_raw
        linkedin = str(pub.get("linkedin") or "").strip()
        if linkedin:
            entry["linkedin"] = linkedin
        gh_user = str(src.get("github_username") or "").strip().lstrip("@")
        if gh_user:
            entry["github"] = f"https://github.com/{gh_user}"

    bio = re.sub(r"\s+", " ", str(pub.get("bio") or "")).strip()
    if bio and bio.lower() != full_name.lower():
        entry["note"] = bio

    pref = str(src.get("preferred_name") or "").strip()
    if pref and pref.lower() not in full_name.lower():
        last_name = full_name.split()[-1]
        entry["aliases"] = [f"{pref} {last_name}".strip()]

    if existing:
        for k in PRESERVED_MANUAL_KEYS:
            if k in existing and existing[k] not in (None, "", []):
                entry.setdefault(k, existing[k])

    return gid, entry


def format_scalar(val) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    s = str(val)
    if re.search(r"[:#\"'\\{}\[\],&*?|>!%@`\n]", s) or s != s.strip() or not s:
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


def dump_member_lines(member: dict, base_indent: str = "      ") -> list[str]:
    lines = []
    keys = [k for k in MEMBER_FIELD_ORDER if k in member]
    keys.extend(k for k in member if k not in keys)
    field_indent = base_indent + "  "
    for idx, k in enumerate(keys):
        v = member[k]
        prefix = f"{base_indent}- " if idx == 0 else field_indent
        if isinstance(v, list):
            if k == "aliases":
                quoted = ", ".join(f'"{str(item).replace(chr(34), chr(92) + chr(34))}"' for item in v)
                lines.append(f"{prefix}{k}: [{quoted}]")
            else:
                lines.append(f"{prefix}{k}:")
                for item in v:
                    lines.append(f"{field_indent}  - {format_scalar(item)}")
        else:
            lines.append(f"{prefix}{k}: {format_scalar(v)}")
    return lines


def dump_people_yaml(out_doc: dict) -> str:
    lines = [HEADER.rstrip("\n"), "", "groups:"]
    for g in out_doc["groups"]:
        gid = g["id"]
        if gid in GROUP_COMMENTS:
            lines.extend(GROUP_COMMENTS[gid])
        lines.append(f"  - id: {gid}")
        lines.append(f"    title: {format_scalar(g['title'])}")
        members = g.get("members") or []
        if not members:
            lines.append("    members: []")
        else:
            lines.append("    members:")
            for m in members:
                lines.extend(dump_member_lines(m, base_indent="      "))
        lines.append("")

    for bucket, comments in (("affiliates", AFFILIATES_COMMENT), ("alumni", ALUMNI_COMMENT)):
        lines.extend(comments)
        sec = out_doc[bucket]
        lines.append(f"{bucket}:")
        lines.append(f"  title: {format_scalar(sec['title'])}")
        members = sec.get("members") or []
        if not members:
            lines.append("  members: []")
        else:
            lines.append("  members:")
            for m in members:
                lines.extend(dump_member_lines(m, base_indent="    "))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sync lab-admin/members into _data/people.yml.")
    ap.add_argument("--members-dir", default=DEFAULT_MEMBERS_DIR,
                    help="Path to lab-admin/members directory.")
    ap.add_argument("--out", default=PEOPLE_YML, help="Output _data/people.yml path.")
    args = ap.parse_args(argv)

    existing_doc = load_yaml(args.out) if os.path.exists(args.out) else {}
    existing_by_name = index_existing(existing_doc)

    # Preserve PI group as configured in _data/people.yml.
    pi_members = []
    for g in existing_doc.get("groups") or []:
        if g.get("id") == "pi":
            pi_members = g.get("members") or []
            break

    grouped: dict[str, list[dict]] = {gid: [] for gid, _ in GROUP_META}
    grouped["pi"] = list(pi_members)

    admin_members = load_admin_members(args.members_dir)
    for src in admin_members:
        key = src["full_name"].strip().lower()
        gid, entry = build_member_entry(src, existing_by_name.get(key))
        grouped.setdefault(gid, []).append(entry)

    for gid in grouped:
        if gid != "pi":
            grouped[gid].sort(key=lambda m: m["name"].split()[-1].lower())

    out_doc = {
        "groups": [
            {"id": gid, "title": title, "members": grouped.get(gid, [])}
            for gid, title in GROUP_META
        ],
        "affiliates": existing_doc.get("affiliates") or {"title": "Collaborators", "members": []},
        "alumni": existing_doc.get("alumni") or {"title": "Alumni", "members": []},
    }
    if out_doc["affiliates"].get("members") is None:
        out_doc["affiliates"]["members"] = []
    if out_doc["alumni"].get("members") is None:
        out_doc["alumni"]["members"] = []

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(dump_people_yaml(out_doc))

    total = sum(len(grouped.get(gid, [])) for gid, _ in GROUP_META if gid != "pi")
    print(f"Synced {total} student/researcher profile(s) into {args.out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
