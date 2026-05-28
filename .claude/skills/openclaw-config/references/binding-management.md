# Binding 管理指南

Bindings 控制消息如何路由到不同的 agents。

## 什么是 Binding？

Binding 是一条路由规则，告诉 OpenClaw：
- 当收到来自**特定渠道**的消息时
- 从**特定账户**发来的
- 可选：发给**特定对端**（用户/群组/频道）
- 应该路由到**哪个 agent**

## 添加 Binding

### 基本用法

```bash
python3 scripts/add_binding.py <agent-id> <channel> <account-id>
```

示例：
```bash
# Telegram bot → agent
python3 scripts/add_binding.py project-manager telegram project-manager

# WhatsApp 账户 → agent
python3 scripts/add_binding.py work whatsapp biz
```

### Peer-specific Binding

路由特定的用户、群组或频道到某个 agent：

```bash
python3 scripts/add_binding.py <agent-id> <channel> <account-id> --peer-kind <kind> --peer-id <id>
```

Peer kinds:
- `dm` - 私信（Direct Message）
- `group` - 群组
- `channel` - 频道

示例：
```bash
# 特定 WhatsApp 群组 → family agent
python3 scripts/add_binding.py family whatsapp personal --peer-kind group --peer-id "120363999@g.us"

# 特定 Telegram 用户 → support agent
python3 scripts/add_binding.py support telegram default --peer-kind dm --peer-id "+15555550123"

# 特定 Discord 频道 → dev agent
python3 scripts/add_binding.py dev discord default --peer-kind channel --peer-id "123456789"
```

## Binding 优先级

Bindings 按**最具体优先**的规则匹配：

1. **Peer 匹配** - 精确的用户/群组/频道 ID（最高优先级）
2. **Guild ID** - Discord 服务器
3. **Team ID** - Slack 工作空间
4. **Account ID** - 渠道账户
5. **Channel** - 渠道级别
6. **Default agent** - 默认 agent（最低优先级）

### 示例：优先级顺序

```json
{
  "bindings": [
    // 1. 最高优先级：特定群组
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "accountId": "personal",
        "peer": { "kind": "group", "id": "120363999@g.us" }
      }
    },
    // 2. 中等优先级：账户级别
    {
      "agentId": "work",
      "match": {
        "channel": "whatsapp",
        "accountId": "biz"
      }
    },
    // 3. 低优先级：渠道级别
    {
      "agentId": "main",
      "match": {
        "channel": "whatsapp"
      }
    }
  ]
}
```

## 查看 Bindings

```bash
python3 scripts/list_config.py --bindings
```

或使用 OpenClaw CLI：
```bash
openclaw agents list --bindings
```

## 常见场景

### 场景 1：多个 Telegram Bots

每个 bot 路由到不同的 agent：

```bash
python3 scripts/add_binding.py main telegram default
python3 scripts/add_binding.py project-manager telegram project-manager
python3 scripts/add_binding.py support telegram support-bot
```

### 场景 2：按渠道分割

不同渠道使用不同的 agent：

```bash
# WhatsApp → 日常助手
python3 scripts/add_binding.py chat whatsapp personal

# Telegram → 深度工作助手
python3 scripts/add_binding.py opus telegram default

# Discord → 开发助手
python3 scripts/add_binding.py dev discord default
```

### 场景 3：家庭群组专用 Agent

特定群组使用专用 agent，其他使用默认 agent：

```bash
# 家庭群组 → family agent
python3 scripts/add_binding.py family whatsapp personal --peer-kind group --peer-id "120363999@g.us"

# 其他所有 WhatsApp → main agent
python3 scripts/add_binding.py main whatsapp personal
```

### 场景 4：工作和个人分离

```bash
# 工作 WhatsApp 账户 → work agent
python3 scripts/add_binding.py work whatsapp biz

# 个人 WhatsApp 账户 → personal agent
python3 scripts/add_binding.py personal whatsapp personal
```

## Binding 配置结构

Bindings 存储在 `openclaw.json` 的 `bindings` 数组中：

```json
{
  "bindings": [
    {
      "agentId": "project-manager",
      "match": {
        "channel": "telegram",
        "accountId": "project-manager"
      }
    },
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "accountId": "personal",
        "peer": {
          "kind": "group",
          "id": "120363999@g.us"
        }
      }
    }
  ]
}
```

## 删除 Binding

目前需要手动编辑 `~/.openclaw/openclaw.json`：

1. 备份配置：`cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup`
2. 编辑文件，删除相应的 binding 对象
3. 重启 OpenClaw：`openclaw gateway restart`

## 故障排查

**消息没有路由到正确的 agent：**

1. 检查 binding 是否存在：
   ```bash
   python3 scripts/list_config.py --bindings
   ```

2. 检查 binding 顺序（更具体的应该在前面）

3. 验证 agent ID 和 account ID 是否匹配：
   ```bash
   python3 scripts/list_config.py
   ```

4. 查看日志：
   ```bash
   openclaw gateway logs | grep -i routing
   ```

5. 重启 OpenClaw：
   ```bash
   openclaw gateway restart
   ```

**多个 agents 响应同一条消息：**

这不应该发生。每条消息只会路由到一个 agent。如果出现这种情况：
- 检查是否配置了广播组（broadcast groups）
- 查看日志确认路由行为

**Peer-specific binding 不工作：**

1. 确认 peer ID 格式正确：
   - WhatsApp 群组：`120363999@g.us`
   - Telegram 群组：`-1001234567890`
   - 用户 ID：`+15555550123` 或数字 ID

2. 确认 peer kind 正确：`dm`、`group` 或 `channel`

3. 检查 binding 是否在账户级 binding 之前（优先级）

## 参考

- [Agent 创建](agent-creation.md) - 创建 agent 时自动配置 binding
- [配置指南](config-guide.md) - 完整的配置参考
- [CLI 参考](cli-reference.md) - OpenClaw CLI 命令

官方文档：
- `~/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/docs/zh-CN/concepts/multi-agent.md`
- `~/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/docs/zh-CN/channels/channel-routing.md`
