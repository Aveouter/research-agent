# TOOLS.md - Local Notes

Judge 通常只需要读取 main agent 传入的文本、rubric 和 candidate answer。

如果需要检查文件，优先读取 main agent 明确提供的路径；不要自行扩大到无关目录。

## Wiki 工具（memory-wiki，isolated 模式，只读）

Judge 不修改 wiki。但当 rubric 要求 fact-check 或核对 anchor 引用时，可只读地用以下工具：

- `wiki_status` — 必要时确认 vault 在线
- `wiki_search` — 按 claim / 论文标题 / 作者搜既有页面，核对 candidate 答案的事实
- `wiki_get` — 按 main agent 给出的页面 id/path 读原文
- `wiki_lint` — 如要给评分理由列出 provenance 问题，可跑一次拿到结构化结果

**禁止** 调用 `wiki_apply`：judge 角色只判分，不写 wiki。发现的 wiki 缺陷写进评审意见，让 main agent 派 curate 修。

## 文件操作

- 仅限 `memory/` 目录写入（过程记录）；不创建 `outputs/` 或其他 agent 可读取的产物文件
- **不调用** `sessions_spawn`：本 agent 不派生子 agent
