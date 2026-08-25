# cc-switch-cli-setup

用 [cc-switch](https://github.com/SaladDay/cc-switch-cli) 统一安装并配置 CLI coding agents：**Codex**、**Claude Code**，以及未来可能支持的 **Grok Build**。

把第三方中转（OpenAI 兼容 / Anthropic 兼容）的 **API Key、Base URL、模型名** 写进各 CLI 的 live 配置，必要时自动开本地代理做协议转换。

## 什么时候用

- 「帮我装一下 Claude Code / Codex，再配上这个 key」
- 「用 cc-switch 切换供应商 / 中转站」
- 「Claude 报连不上 `api.anthropic.com`，但我想走自建 / 第三方 API」

## Agent 会怎么做

1. **先装工具**：`cc-switch` + 你指定的 CLI（不猜密钥）
2. **再问你要配置**（缺一不可）：
   - 应用：`codex` / `claude` / 两者（或已支持的 `grokbuild`）
   - API Key
   - Base URL（可带或不带 `/v1`）
   - 模型名（如 `grok-4.6`）
3. **探测接口格式**（Chat / Responses / Anthropic Messages），选对 `--api-format`
4. **`provider add` + `switch`**，Claude 走 OpenAI 兼容时启用本地 proxy
5. **冒烟测试**后汇报结果（密钥只显示末 4 位）

详细步骤见 [`SKILL.md`](SKILL.md)；排障与备选安装见 [`reference.md`](reference.md)。

## 从本 Hub 安装

```bash
cd ~/my-skills-hub   # 或你的 clone 路径
git pull
./scripts/install.sh --only cc-switch-cli-setup

# 指定目标目录：
./scripts/install.sh --target claude --only cc-switch-cli-setup   # ~/.claude/skills
./scripts/install.sh --target codex  --only cc-switch-cli-setup   # ~/.codex/skills
./scripts/install.sh --target cursor --only cc-switch-cli-setup   # ~/.cursor/skills
```

安装后重启 / 重新加载 agent，然后直接说例如：

> 用 cc-switch 给 Codex 和 Claude 配一下中转

## 支持范围

| 应用 | cc-switch `--app` | 说明 |
|------|-------------------|------|
| Codex | `codex` | 直接写 `~/.codex/config.toml` + `auth.json` |
| Claude Code | `claude` | Anthropic 原生可直连；OpenAI 兼容需本地 proxy（默认 `127.0.0.1:15721`） |
| Grok Build | （视版本） | 使用前先确认当前 cc-switch 是否已支持；未支持则跳过并说明 |

## 你需要准备什么

```text
1. 要配置的应用：codex / claude / 两者
2. API Key
3. Base URL（例如 https://example.com 或 https://example.com/v1）
4. 模型名（例如 grok-4.6）
5. （可选）供应商显示名 / ID
```

不要把密钥提交进 git；聊天里贴过的 key 建议事后在中转站轮换。

## 常见注意点

- **Base URL** 通常需要带 `/v1`，否则可能打到官网 HTML 而不是 API。
- Claude 若出现 `Unable to connect to api.anthropic.com`：多半是首启 onboarding；skill 会跳过并指到本地 proxy。
- Codex 对自定义模型可能提示 `Model metadata not found`：一般仍可用，可用可选 `model_catalog_json` 消警告（见 `reference.md`）。
- 模型口头自称「GPT-x」往往是 Codex 系统提示人设，以状态栏 / 账单上的 model id 为准。

## 文件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | Agent 执行流程（硬规则 + checklist） |
| `reference.md` | 安装备选、proxy 排障、验证矩阵 |
| `README.md` | 给人看的说明（本文件） |

## License

与 [my-skills-hub](https://github.com/Laip11/my-skills-hub) 仓库一致。上游工具各自遵循其许可证（cc-switch MIT 等）。
