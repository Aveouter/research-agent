# Agent 创建指南

完整的 OpenClaw agent 创建流程。

## 快速创建

使用 `create_agent.py` 一步完成所有配置：

```bash
python3 scripts/create_agent.py <agent-id> <agent-name> <bot-token> [workspace-path]
```

这个脚本会自动：
1. ✅ 添加 Telegram bot 账号
2. ✅ 注册新 agent
3. ✅ 配置 binding（自动路由）
4. ✅ 备份配置文件

## 参数说明

- `agent-id` (必需) - Agent 的唯一标识符（小写，可用连字符）
- `agent-name` (必需) - Agent 的显示名称（任意字符）
- `bot-token` (必需) - Telegram bot token（从 @BotFather 获取）
- `workspace-path` (可选) - 工作空间路径（默认：`~/.openclaw/workspace/<agent-id>`）
- `telegram-account-id` (可选) - Telegram 账户 ID（默认：与 agent-id 相同）

## 创建流程

### 1. 获取 Telegram Bot Token

1. 在 Telegram 中找到 **@BotFather**
2. 发送 `/newbot` 命令
3. 按提示设置 bot 名称和用户名
4. 复制 token（格式：`123456:ABC-DEF...`）

### 2. 运行创建脚本

```bash
python3 scripts/create_agent.py project-manager "项目管理助手" "8794745677:AAGusS8oiSXX8NK1F-CzLKqsGYWQGmDpvw8"
```

输出示例：
```
🤖 Creating agent: project-manager
   Name: 项目管理助手
   Bot token: 8794745677:AAGusS8oi...

✓ Added Telegram account: project-manager
✓ Added agent: project-manager
  Name: 项目管理助手
  Workspace: /home/user/.openclaw/workspace/project-manager
✓ Added binding: project-manager → project-manager
✓ Configuration saved (backup: ~/.openclaw/openclaw.json.backup-agent-creator)

✅ Agent created successfully!
```

### 3. 创建工作空间

```bash
mkdir -p ~/.openclaw/workspace/project-manager
```

### 4. 添加配置文件

使用 `assets/` 目录中的模板：

```bash
cd ~/.openclaw/workspace/project-manager

# 复制模板
cp /path/to/skill/assets/SOUL.md.template SOUL.md
cp /path/to/skill/assets/AGENTS.md.template AGENTS.md
cp /path/to/skill/assets/USER.md.template USER.md

# 编辑模板，替换占位符
# {{agent_name}} → 项目管理助手
# {{agent_purpose}} → 项目管理
# {{workspace_path}} → /home/user/.openclaw/workspace/project-manager
```

### 5. 重启 OpenClaw

```bash
openclaw gateway restart
```

### 6. 测试 Bot

在 Telegram 中搜索你的 bot，发送消息测试。

## 配置文件模板

### SOUL.md

定义 agent 的性格和行为：

```markdown
# SOUL.md - {{agent_name}}的灵魂

## 我是谁
我是{{agent_name}}，专注于{{agent_purpose}}。

## 核心特质
**专业高效** - 我以结果为导向，注重效率和准确性。
**主动负责** - 我会主动完成任务，而不是被动等待指令。

## 工作风格
[根据 agent 的具体特点填写]

## 边界
- 专注于{{agent_purpose}}相关任务
- 保持客观中立，基于事实做决策
```

### AGENTS.md

描述 agent 的职责和工作流程：

```markdown
# AGENTS.md - {{agent_name}}工作空间

## 身份
我是{{agent_name}}，专门负责{{agent_purpose}}。

## 职责
[根据 agent 的具体用途填写职责]

## 工作方式
### 每次会话开始
1. 读取 SOUL.md 了解自己的身份
2. 读取 USER.md 了解用户信息
3. 检查最近的工作记录

## 工作空间
- **本地路径：** {{workspace_path}}
- **Telegram Bot：** {{agent_name}}
```

### USER.md

存储用户信息和偏好：

```markdown
# USER.md - 关于用户

- **用户名称：** [待填写]
- **时区：** Asia/Shanghai (UTC+8)
- **语言：** 中文

## 沟通方式
- **Telegram：** {{agent_name}} Bot
- **工作空间：** {{workspace_path}}
```

## 高级选项

### 自定义工作空间路径

```bash
python3 scripts/create_agent.py my-agent "我的助手" "token" "/custom/path/workspace"
```

### 自定义 Telegram 账户 ID

```bash
python3 scripts/create_agent.py my-agent "我的助手" "token" "/path" "custom-account-id"
```

## 故障排查

**Agent 已存在：**
- 选择不同的 agent-id
- 或删除现有 agent：`openclaw agents delete <agent-id>`

**Telegram 账户已存在：**
- 选择不同的 telegram-account-id
- 或删除现有账户（手动编辑配置）

**Bot 不响应：**
1. 检查 OpenClaw 是否重启：`openclaw gateway status`
2. 查看日志：`openclaw gateway logs`
3. 验证 bot token 是否正确
4. 确认工作空间目录存在
5. 检查配置文件是否创建

**配置验证失败：**
- 恢复备份：`cp ~/.openclaw/openclaw.json.backup-agent-creator ~/.openclaw/openclaw.json`
- 运行诊断：`openclaw doctor`

## 使用 OpenClaw CLI

也可以使用官方 CLI 命令创建 agent：

```bash
# 添加 agent
openclaw agents add project-manager --workspace ~/.openclaw/workspace-project

# 设置身份
openclaw agents set-identity --agent project-manager --name "项目管理助手"

# 手动添加 binding
python3 scripts/add_binding.py project-manager telegram project-manager
```

但使用 `create_agent.py` 更方便，一步完成所有配置。

## 参考

- [Binding 管理](binding-management.md) - 了解如何管理路由规则
- [配置指南](config-guide.md) - 完整的配置参考
- [CLI 参考](cli-reference.md) - OpenClaw CLI 命令
