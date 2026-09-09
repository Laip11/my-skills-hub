# Codex、Claude Code 与 Cursor 兼容性

本仓库中的 hub-owned Skill 使用 Agent Skills 通用结构：每个 Skill 目录以 `SKILL.md` 为入口，并可包含 `scripts/`、`references/` 和 `assets/`。共享逻辑只维护一份，不同 coding agent 的差异由安装路径和调用方式处理。

## 推荐安装

```bash
# Codex + Cursor 共用 ~/.agents/skills
./scripts/install.sh --target shared

# Claude Code
./scripts/install.sh --target claude

# 三者一次安装
./scripts/install.sh --target all
```

安装器默认创建符号链接，仓库更新后无需再次复制。需要独立副本时使用 `--mode copy`。

## Agent 对照

| Agent | 用户级目录 | 项目级目录 | 显式调用 |
|---|---|---|---|
| Codex | `~/.agents/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | `$skill-name` |
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `/skill-name` |
| Cursor | `~/.agents/skills/<name>/SKILL.md` 或 `~/.cursor/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` 或 `.cursor/skills/<name>/SKILL.md` | `/skill-name` |

Cursor 能直接读取 `.agents/skills`，因此 `shared` 是同时服务 Codex 与 Cursor 的推荐位置。若需要 Cursor Cloud Agents 的个人 Skill 同步功能，则使用 `--target cursor` 安装到 `~/.cursor/skills`。

## 调用示例

Codex：

```text
$paper-evidence-research 调研 LLM Agent 的技能内化方法
$research-visual-report 把 report.md 构建成可交互网页
```

Claude Code 或 Cursor：

```text
/paper-evidence-research 调研 LLM Agent 的技能内化方法
/research-visual-report 把 report.md 构建成可交互网页
```

也可以使用自然语言请求，由 Agent 根据 `description` 自动选择 Skill。

## 平台特有文件

`agents/openai.yaml` 只为 Codex / ChatGPT 桌面端提供展示元数据，不承载研究流程。Claude Code 与 Cursor 即使忽略该文件，也会从同一份 `SKILL.md`、脚本和参考资料中获得完整能力。

## 官方参考

- [OpenAI：Build skills](https://developers.openai.com/codex/skills)
- [Anthropic：Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Cursor：Agent Skills](https://cursor.com/docs/skills)
