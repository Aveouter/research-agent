# OpenClaw CLI 参考

## Agent 管理

### `openclaw agents`

管理隔离的智能体（工作区 + 认证 + 路由）。

**列出所有 agents：**
```bash
openclaw agents list
openclaw agents list --bindings  # 显示 bindings
```

**添加新 agent：**
```bash
openclaw agents add <agent-id> --workspace <path>
```

示例：
```bash
openclaw agents add work --workspace ~/.openclaw/workspace-work
openclaw agents add family --workspace ~/.openclaw/workspace-family
```

**设置 agent 身份：**
```bash
openclaw agents set-identity --agent <agent-id> [options]
```

选项：
- `--name <name>` - 显示名称
- `--emoji <emoji>` - 表情符号
- `--avatar <path>` - 头像路径（相对于工作空间）
- `--theme <theme>` - 主题描述
- `--from-identity` - 从工作空间的 IDENTITY.md 读取

示例：
```bash
openclaw agents set-identity --agent main --name "OpenClaw" --emoji "🦞"
openclaw agents set-identity --workspace ~/.openclaw/workspace --from-identity
```

**删除 agent：**
```bash
openclaw agents delete <agent-id>
```

## 配置管理

### `openclaw config`

通过路径获取/设置/取消设置配置值。

**获取配置值：**
```bash
openclaw config get <path>
```

示例：
```bash
openclaw config get agents.defaults.workspace
openclaw config get agents.list[0].id
openclaw config get channels.telegram.accounts.default.botToken
```

**设置配置值：**
```bash
openclaw config set <path> <value> [--json]
```

示例：
```bash
openclaw config set agents.defaults.workspace "~/.openclaw/workspace"
openclaw config set gateway.port 19001 --json
openclaw config set agents.list[0].tools.exec.node "node-id"
```

**取消设置配置值：**
```bash
openclaw config unset <path>
```

示例：
```bash
openclaw config unset tools.web.search.apiKey
```

### 路径表示法

使用点号或括号表示法：
- `agents.defaults.workspace`
- `agents.list[0].id`
- `channels.telegram.accounts.default.botToken`

### 值解析

- 值会尽可能解析为 JSON5
- 否则被视为字符串
- 使用 `--json` 强制 JSON5 解析

## Gateway 管理

### `openclaw gateway`

管理 Gateway 服务。

**启动/停止/重启：**
```bash
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
```

**查看状态：**
```bash
openclaw gateway status
```

**查看日志：**
```bash
openclaw gateway logs
openclaw gateway logs --follow  # 实时跟踪
```

## 诊断

### `openclaw doctor`

检查配置和系统状态。

**检查问题：**
```bash
openclaw doctor
```

**自动修复：**
```bash
openclaw doctor --fix
openclaw doctor --yes  # 不询问直接修复
```

### `openclaw status`

显示系统状态概览。

```bash
openclaw status
```

## Channel 管理

### `openclaw channels`

列出和管理 channels。

```bash
openclaw channels list
```

## 配置向导

### `openclaw configure`

交互式配置向导。

```bash
openclaw configure
```

或者：
```bash
openclaw config  # 不带子命令
```

## 常用工作流程

### 创建新 Agent

```bash
# 1. 添加 agent
openclaw agents add project-manager --workspace ~/.openclaw/workspace-project

# 2. 设置身份（可选）
openclaw agents set-identity --agent project-manager --name "项目管理助手"

# 3. 添加 binding（使用 skill 脚本）
python3 scripts/add_binding.py project-manager telegram project-manager

# 4. 重启
openclaw gateway restart
```

### 修改配置

```bash
# 1. 查看当前值
openclaw config get agents.defaults.workspace

# 2. 修改值
openclaw config set agents.defaults.workspace "~/new-workspace"

# 3. 重启
openclaw gateway restart
```

### 调试路由问题

```bash
# 1. 列出 agents 和 bindings
openclaw agents list --bindings

# 2. 检查配置
python3 scripts/list_config.py

# 3. 查看日志
openclaw gateway logs

# 4. 运行诊断
openclaw doctor
```

## 注意事项

1. **配置更改后需要重启** - 大多数配置更改需要重启 Gateway 才能生效
2. **备份配置** - 修改配置前建议备份 `~/.openclaw/openclaw.json`
3. **验证配置** - 使用 `openclaw doctor` 验证配置正确性
4. **查看日志** - 遇到问题时查看日志可以快速定位原因
5. **使用 CLI 优先** - OpenClaw 的内置 CLI 命令比手动编辑配置文件更安全

## 参考

完整 CLI 文档：
- `openclaw help`
- `openclaw <command> --help`
- `~/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/docs/zh-CN/cli/`
