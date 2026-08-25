# Skills Hub

个人 Agent Skills 合集：以 git submodule 收录上游仓库，提供分类索引与安装入口。各 skill 相互独立，保持原仓库结构。

机器可读索引见 [`catalog.yaml`](catalog.yaml)。

## 目录

| 分类 | Skill | 上游 |
|------|-------|------|
| 论文写作 / 审稿 | [anti-defensive-writing](skills/anti-defensive-writing) | [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing) |
| 论文写作 / 审稿 | [academic-research-skills](skills/academic-research-skills) | [imbad0202/academic-research-skills](https://github.com/imbad0202/academic-research-skills) |
| 论文写作 / 审稿 | [citation-check-skill](skills/citation-check-skill) | [serenakeyitan/citation-check-skill](https://github.com/serenakeyitan/citation-check-skill) |
| 论文写作 / 审稿 | [mean-reviewer-skill](skills/mean-reviewer-skill) | [xz-liu/mean-reviewer-skill](https://github.com/xz-liu/mean-reviewer-skill) |
| 论文写作 / 审稿 | [awesome-rebuttal](skills/awesome-rebuttal) | [xiongqi123123/awesome-rebuttal](https://github.com/xiongqi123123/awesome-rebuttal) |
| 图表 | [paper-plot-skills](skills/paper-plot-skills) | [Trae1ounG/paper-plot-skills](https://github.com/Trae1ounG/paper-plot-skills) |
| 图表 | [drawio-skill](skills/drawio-skill) | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) |
| 论文传播 | [paper2anything](skills/paper2anything) | [QuZhan51496/paper2anything](https://github.com/QuZhan51496/paper2anything) |
| 演示稿 / PPT | [visual-deck](skills/visual-deck) | [xiaomoBoy/visual-deck](https://github.com/xiaomoBoy/visual-deck) |
| 演示稿 / PPT | [ppt-master](skills/ppt-master) | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) |
| 演示稿 / PPT | [frontend-slides](skills/frontend-slides) | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) |
| UI / 设计 | [design-skills](skills/design-skills) | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| 编程 / Agent 行为 | [karpathy-guidelines](skills/karpathy-guidelines) | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) |
| Prompt 工程 | [prompt-master](skills/prompt-master) | [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) |
| 工具 / CLI 配置 | [cc-switch-cli-setup](skills/cc-switch-cli-setup) | hub-owned（本仓库） |

## 快速开始

```bash
# 克隆（含子模块）
git clone --recurse-submodules https://github.com/<YOU>/skills-hub.git
cd skills-hub

# 已克隆时初始化子模块
git submodule update --init --recursive

# 安装到本机 skills 目录（默认 Cursor）
./scripts/install.sh                  # ~/.cursor/skills
./scripts/install.sh --target claude  # ~/.claude/skills
./scripts/install.sh --target codex   # ~/.codex/skills
./scripts/install.sh --only visual-deck,paper-plot-skills
```

同步上游更新：

```bash
./scripts/sync.sh
```

## Skill 说明

### 论文写作 / 审稿

| Skill | 说明 |
|-------|------|
| anti-defensive-writing | 收敛 defensiveness，强化 claim-forward 表述 |
| academic-research-skills | 研究全流程：research → write → review → revise → finalize |
| citation-check-skill | 校验 LLM 输出中的引用真实性 |
| mean-reviewer-skill | 严苛审稿人模拟，用于投稿前压力测试 |
| awesome-rebuttal | Rebuttal：审稿意见分析、实验分流、回复起草与安全门控 |

### 图表

| Skill | 说明 |
|-------|------|
| paper-plot-skills | 顶会风格图表绘制与复现（按风格填数据 / 从截图复现） |
| drawio-skill | 自然语言 / 代码 / 基础设施 → 可编辑 `.drawio`，并可导出 PNG / SVG / PDF / JPG |

### 论文传播

| Skill | 说明 |
|-------|------|
| paper2anything | 论文 PDF → slides / poster / webpage / 小红书 / 公众号 |

### 演示稿 / PPT

| Skill | 说明 |
|-------|------|
| visual-deck | 选题 / 大纲 → 图文混合全屏 HTML 演示稿（可导出 MP4） |
| ppt-master | 文档 / 选题 → 原生 PPTX（SVG → DrawingML） |
| frontend-slides | 基于前端能力生成网页幻灯片 |

### UI / 设计

| Skill | 说明 |
|-------|------|
| design-skills | Design Engineering（含 `apple-design`）：动画、界面与 UI 库选型 |

### 编程 / Agent 行为

| Skill | 说明 |
|-------|------|
| karpathy-guidelines | 减少错误假设、过度设计和无关改动，用可验证的成功标准驱动编程 |

### Prompt 工程

| Skill | 说明 |
|-------|------|
| prompt-master | 为具体 AI 工具生成、修正和适配精准 Prompt |

### 工具 / CLI 配置

| Skill | 说明 |
|-------|------|
| cc-switch-cli-setup | 安装/配置 cc-switch，并为 Codex、Claude Code（及未来 Grok Build）接入第三方 API Key、Base URL 与模型 |

亦可直接安装上游：

```bash
npx skills@latest add emilkowalski/skills
```

## 使用链路

```text
写稿 → anti-defensive-writing + citation-check-skill
     → mean-reviewer-skill（投稿前）
     → awesome-rebuttal（审稿回复）

论文图表 → paper-plot-skills
流程图 / 架构图 → drawio-skill
传播 → paper2anything
演示 → visual-deck / frontend-slides / ppt-master
界面 → design-skills
写代码 → karpathy-guidelines
写 Prompt → prompt-master
CLI  → cc-switch-cli-setup（Codex / Claude Code 供应商切换）
```

## 仓库结构

```text
skills-hub/
├── README.md
├── catalog.yaml          # 索引元数据
├── skills/               # 各 skill 的 git submodule
└── scripts/
    ├── install.sh        # 安装到本机 skills 目录（默认 symlink）
    └── sync.sh           # 同步各 submodule
```

## 说明

- 各子目录对应独立上游仓库，许可证与用法以该仓库的 README / `SKILL.md` 为准。
- `install.sh` 默认以 symlink 安装，便于跟随 `sync.sh` 更新。
