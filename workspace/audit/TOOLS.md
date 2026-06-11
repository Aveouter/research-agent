# TOOLS.md - 本地说明

这个工作区主要依赖 skill 工作流和上游产出的读取，本身没有额外的设备或账号约定。

## 约定

- 输出优先使用 Markdown，方便直接落到 Obsidian 或仓库里。
- 评估报告要有可操作性：每条问题必须落到具体文件、具体段落。
- 可复用的审计经验放进 `MEMORY.md`。

## 工作区内技能

- `paper-pipeline-quality-auditor`（S6）

> S2–S5 的执行以及 Wiki 整理都不属于本 agent 的技能范围，分别由 `extract`/`critic`/`design`/`spec` 和 `ingest`/`curate` 子 agent 负责。

## Wiki 工具（memory-wiki，read-only）

本 agent 是审计员，只读取 wiki 内容评估上游产出，**绝不写入**：

- `wiki_status` — 确认 vault 在线且 isolated 模式下可读。
- `wiki_search` — 搜既有论文条目 / 相关 claim，用于比对上游引用是否与 wiki 一致。
- `wiki_get` — 按 id/path 拉单页详情，用于核验上游 S2–S5 引用的事实是否准确。
- `wiki_lint` — 引用 wiki 内容前如果担心 provenance，跑一次确认没有 contradiction 或 open question 影响上游结论。

如果发现 wiki 缺条目或需要更新，**不要自己用 `wiki_apply`**，把缺口写回 main agent，由 main 委派 curate 处理。

Dashboard（`reports/open-questions.md`、`reports/contradictions.md` 等）用 `wiki_get` 读。

## 文件操作

- 读：上游各阶段产出内容（main agent 在 task 中传递）
- 写：仅 `memory/YYYY-MM-DD.md` 过程记录，不创建 outputs/ 或其他产物文件
- **不修改**任何上游阶段产出

## 不可用工具

- **不调用 `sessions_spawn`** — 本 agent 不派生子 agent
- **不调用 `wiki_apply`** — 只读 wiki，不写
