# TOOLS.md - 本地说明

## 约定

- 输出优先使用 Markdown，方便直接落到 Obsidian 或仓库里
- 严格遵循 `paper-experiment-deep-extractor` skill 的 11 节输出结构
- 可复用的流程经验放进 `MEMORY.md`

## 工作区内技能

- `paper-experiment-deep-extractor`（S2：实验深度提取）

## Wiki 工具（memory-wiki，isolated 模式，只读）

- `wiki_status` — 确认 vault 在线且 isolated 模式下可读
- `wiki_search` — 搜既有论文条目 / 相关 claim / 已记录的实验设计
- `wiki_get` — 按 id/path 拉单页详情，作为实验提取的输入
- `wiki_lint` — 引用 wiki 内容前跑一次确认没有 contradiction

> 本 agent **不调用** `wiki_apply`（写入由 ingest/curate 负责）。

## 文件操作

- 仅限本工作区目录：`memory/`
- 产物通过 inline reply 直接返回调用者，不写入文件系统

## 不使用的工具

- `sessions_spawn` — 本 agent **不**派生子 agent，不做跨 agent 编排
- `wiki_apply` — 本 agent **不**修改 wiki
