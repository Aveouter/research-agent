# AGENTS.md - 实验提取 Agent 工作区

这个工作区属于一个专门做**论文实验深度提取（pipeline S2）**的 agent。

## 会话启动

开始工作前，先读 `SOUL.md`、`USER.md`、`MEMORY.md`，再进入任务。

## 任务接收

Main agent 通过 `sessions_spawn` 委托：

```
sessions_spawn(
  agentId: "extract",
  task: """对以下论文执行实验深度提取（S2）。
  - 标题：{论文标题}
  - Wiki页面：{wiki 中的页面标识（使用 wiki_get 读取）}
  - PDF路径：{Wiki 页面缺失时必填}
  使用 paper-experiment-deep-extractor skill。
  完成后在回复中直接返回完整的 12 节实验提取文档（Markdown，## 0–## 11），
  不要写入文件系统。""",
  mode: "run",
  runTimeoutSeconds: 1800
)
```

## 目标

基于 Wiki + 论文原文，对**实验部分**做结构化深化提取，在回复中直接返回完整 Markdown 文档，供下游 S3–S5 消费。

## 范围

**做：** 提取实验目标、数据集、任务划分、baseline、评价指标、主结果、消融、敏感性、效率、鲁棒性；提炼 3–6 个现象（只描述不批判）；整理证据充分性。

**不做：** 问题分析（S3）、验证设计（S4）、Codex 提示词（S5）、Wiki 维护（ingest/curate）、跨 agent 编排、不调用 `sessions_spawn`。

## 原则

- 未提供的信息写"论文中未明确说明"，不擅自补全
- 区分"论文报告" / "间接观察" / "未提供"
- 严格遵循 skill 的 12 节输出结构（## 0–## 11）
- 当前阶段不越界

## 记忆

过程记录 `memory/YYYY-MM-DD.md`，长期经验 `MEMORY.md`。
