# TOOLS.md - 本地说明

## Wiki 工具（只读）

本 agent 通过 memory-wiki 工具只读访问知识库：

- `wiki_status` — 确认 vault 在线且可读
- `wiki_search` — 搜索论文条目、相关 claim、已记录的实验设计
- `wiki_get` — 按 id/path 读取单页详情
- `wiki_lint` — 引用前确认无矛盾

**不使用 `wiki_apply`。** 发现 wiki 缺口时报告给 main agent。

## 文件操作

可在自身 workspace 目录内读写 memory/ 等过程文件。产物（问题分析文档）通过 inline reply 返回调用者。

## 不具备的能力

- 无 `sessions_spawn` — 本 agent 不生成子 agent
- 不编排其他 agent
- 不修改 wiki 知识库
