#!/usr/bin/env python3
"""Narrow lint for the skill packages in this repo.

It only catches things that make a skill fail *silently* after installing it —
nothing about wording, length, formatting or style.

Per `skills/*/SKILL.md`:

  1. frontmatter parses and carries `name` + `description`
  2. `name` matches the directory name
  3. `description` is non-empty and <= 1024 chars
  4. every markdown link resolves to a real file
  5. every backtick reference to a skill-local path (`scripts/`, `references/`,
     `assets/`, `lib/`) exists. Bare names such as `CONTEXT.md` or `docs/` are
     references to the *user's* repo, not ours, so they are not checked.
  6. every `*.sh` passes `bash -n`

Usage (from anywhere):  python3 scripts/lint-skills.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
LOCAL_PREFIXES = ("scripts/", "references/", "assets/", "lib/")
MAX_DESC = 1024

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TICK_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|sh|py|yml|yaml|json|txt))`")

errors: list[str] = []


def err(skill: str, msg: str) -> None:
    errors.append(f"{skill}: {msg}")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Line-based parse — enough for single-line `key: value` fields."""
    m = FM_RE.match(text)
    if not m:
        return None
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line[0] in " \t#" or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip("\"'")
    return fm


def lint_skill(skill_md: Path) -> None:
    name = skill_md.parent.name
    text = skill_md.read_text(encoding="utf-8")

    fm = parse_frontmatter(text)
    if fm is None:
        err(name, "SKILL.md 没有可解析的 frontmatter（文件需以 --- 开头）")
    else:
        if not fm.get("name"):
            err(name, "frontmatter 缺少 name")
        elif fm["name"] != name:
            err(name, f"frontmatter name='{fm['name']}' 与目录名不一致")
        description = fm.get("description", "")
        if not description:
            err(name, "description 缺失或为空")
        elif len(description) > MAX_DESC:
            err(name, f"description 过长（{len(description)} > {MAX_DESC}）")

    for raw in LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        if not (skill_md.parent / target).exists():
            err(name, f"markdown 链接指向不存在的文件: {raw}")

    for raw in TICK_RE.findall(text):
        if not raw.startswith(LOCAL_PREFIXES):
            continue
        if not (skill_md.parent / raw).exists():
            err(name, f"正文引用的本地文件不存在: {raw}")

    for sh in sorted(skill_md.parent.rglob("*.sh")):
        proc = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
        if proc.returncode:
            detail = (proc.stderr.strip().splitlines() or [""])[-1]
            err(name, f"bash -n 失败: {sh.relative_to(ROOT)} :: {detail}")


def main() -> int:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        print(f"✗ 在 {SKILLS} 下没找到任何 skills/*/SKILL.md")
        return 1

    for skill_md in skill_files:
        lint_skill(skill_md)

    if errors:
        unique = list(dict.fromkeys(errors))
        print(f"✗ {len(unique)} 个问题（{len(skill_files)} 个 skill）:\n")
        for item in unique:
            print(f"  - {item}")
        return 1

    print(f"✓ 校验通过：{len(skill_files)} 个 skill 全部 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())