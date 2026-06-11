# TOOLS.md - 本地说明

## Wiki 工具（只读）

本 agent 通过 wiki 工具读取论文信息，不创建或修改 wiki 条目：

- `wiki_status` — 确认 vault 在线且可读
- `wiki_search` — 搜索论文条目、相关 claim、已有实验设计
- `wiki_get` — 按 id/path 拉取单页详情
- `wiki_lint` — 引用 wiki 前确认无 contradiction

发现 wiki 缺失或错误时，在产出中标注，不直接修改。

## 文件操作

可在本 workspace 目录内读写文件（memory/ 等）。产物通过 inline reply 返回调用者，不写入 outputs/。

## 无子 agent 调度

本 agent 不使用 sessions_spawn，不调度其他 agent。

## 工作区内技能

- `paper-validation-experiment-designer`（S4）
