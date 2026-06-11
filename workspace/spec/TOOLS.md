# TOOLS.md

## Wiki 工具（memory-wiki，只读）

- `wiki_status` — 确认 vault 在线
- `wiki_search` — 搜索论文条目、claim、实验设计
- `wiki_get` — 按 id/path 拉取单页详情
- `wiki_lint` — 检查 wiki 内容一致性

## 文件操作

- 可读写本 agent workspace 目录内的文件（`memory/` 等）
- 产物通过 inline reply 直接返回调用者，不写入 outputs/
- 只读访问上游阶段产出（wiki、S2-S4 文档）

## 限制

- 无 `sessions_spawn` 权限——本 agent 不派生子 agent
- 不修改 wiki 或其他 agent 的产出
