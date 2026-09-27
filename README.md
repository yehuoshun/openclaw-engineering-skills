# OpenClaw Engineering Skills

三个面向 OpenClaw（及任何支持 `SKILL.md` 格式的 agent）的工程类 skill，从 [mattpocock/skills](https://github.com/mattpocock/skills)（MIT License）移植，重写为 OpenClaw 原生格式。

原项目是 Claude Code / OpenAI Codex 的 skill 格式（`SKILL.md` 薄壳 + `agents/openai.yaml` 间接调用层），本仓库把核心 prompt 直接落到 `SKILL.md` 正文 + `references/`，去掉了原格式的间接调用与 `openai.yaml` 依赖。

## 包含的 Skills

| Skill | 用途 |
|-------|------|
| `diagnosing-bugs` | 硬骨头 bug / 性能回退的六阶段诊断闭环：先建能变红的反馈回路，再复现最小化 → 假设 → 定位 → 修复 → 回归 |
| `tdd` | 测试驱动开发（red → green）：seam 概念、反模式清单、mock 边界 |
| `code-review` | 双轴审查（Standards 规范 + Spec 需求），并行子代理并排汇报 |

## 安装（OpenClaw）

把 `skills/` 下的目录复制到 OpenClaw 的 skill 目录：

```bash
cp -r skills/* ~/.openclaw/workspace/skills/
```

重启 gateway 或新开会话后生效。

每个 skill 目录自带一份 `LICENSE`（MIT，© Matt Pocock，与仓库根逐字节一致），`cp -r` 会一并装走，满足 MIT 的"声明随副本分发"要求。`scripts/lint-skills.py` 会强制这一点。

## 本地校验

改完 skill 先本地跑一遍（同一个脚本也在 CI 里跑）：

```bash
python3 scripts/lint-skills.py
```

只查会让 skill **静默失效**的东西：frontmatter 可解析、`name` 与目录名一致、`description` 非空且 ≤1024 字符、markdown 链接可解析、正文里 `scripts/` `references/` `assets/` `lib/` 下的引用文件存在、`*.sh` 通过 `bash -n`。不检查措辞与格式。

## 触发方式

直接说需求即可，例如：

- "定位这个 bug" / "debug this" → `diagnosing-bugs`
- "先写测试" / "red-green-refactor" → `tdd`
- "审查这段改动" / "review this PR" → `code-review`

## License

MIT。原始内容版权归 [Matt Pocock](https://github.com/mattpocock)（Copyright (c) 2026 Matt Pocock），本仓库为格式迁移与适配。
