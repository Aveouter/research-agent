# OpenClaw 配置参考

## 多 Agent 配置

### Agent 定义

```json
{
  "agents": {
    "list": [
      {
        "id": "main",           // 必需：agent ID
        "default": true,        // 可选：是否为默认 agent
        "name": "主助手",       // 可选：显示名称
        "workspace": "~/.openclaw/workspace",  // 可选：工作空间路径
        "agentDir": "~/.openclaw/agents/main/agent"  // 可选：状态目录
      }
    ]
  }
}
```

### Bindings（路由规则）

Bindings 用于将入站消息路由到特定的 agent。

**路由优先级（从高到低）：**
1. Peer 匹配（精确的私信/群组/频道 ID）
2. Guild ID（Discord）
3. Team ID（Slack）
4. Account ID 匹配
5. Channel 级匹配
6. 默认 agent

**基本 binding：**

```json
{
  "bindings": [
    {
      "agentId": "project-manager",
      "match": {
        "channel": "telegram",
        "accountId": "project-manager"
      }
    }
  ]
}
```

**Peer-specific binding（更高优先级）：**

```json
{
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "accountId": "personal",
        "peer": {
          "kind": "group",           // "dm" | "group" | "channel"
          "id": "120363999@g.us"     // WhatsApp 群组 ID
        }
      }
    }
  ]
}
```

### Channel 配置

**Telegram：**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "accounts": {
        "default": {
          "botToken": "123456:ABC...",
          "dmPolicy": "pairing"
        },
        "project-manager": {
          "name": "项目管理助手",
          "enabled": true,
          "botToken": "789012:DEF...",
          "dmPolicy": "pairing"
        }
      }
    }
  }
}
```

**WhatsApp：**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "dmPolicy": "pairing",
      "accounts": {
        "personal": {
          "authDir": "~/.openclaw/credentials/whatsapp/personal"
        },
        "biz": {
          "authDir": "~/.openclaw/credentials/whatsapp/biz"
        }
      }
    }
  }
}
```

## 常见配置场景

### 场景 1：多个 Telegram Bot → 多个 Agent

```json
{
  "agents": {
    "list": [
      { "id": "main", "default": true },
      { 
        "id": "project-manager",
        "workspace": "~/projects/docs"
      }
    ]
  },
  "bindings": [
    {
      "agentId": "project-manager",
      "match": {
        "channel": "telegram",
        "accountId": "project-manager"
      }
    },
    {
      "agentId": "main",
      "match": {
        "channel": "telegram",
        "accountId": "default"
      }
    }
  ],
  "channels": {
    "telegram": {
      "accounts": {
        "default": { "botToken": "..." },
        "project-manager": { "botToken": "..." }
      }
    }
  }
}
```

### 场景 2：按渠道分割（WhatsApp 日常 + Telegram 深度工作）

```json
{
  "agents": {
    "list": [
      {
        "id": "chat",
        "model": "anthropic/claude-sonnet-4-5"
      },
      {
        "id": "opus",
        "model": "anthropic/claude-opus-4-5"
      }
    ]
  },
  "bindings": [
    { "agentId": "chat", "match": { "channel": "whatsapp" } },
    { "agentId": "opus", "match": { "channel": "telegram" } }
  ]
}
```

### 场景 3：特定群组路由到专用 Agent

```json
{
  "agents": {
    "list": [
      { "id": "main" },
      { "id": "family" }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "peer": {
          "kind": "group",
          "id": "120363999@g.us"
        }
      }
    },
    {
      "agentId": "main",
      "match": { "channel": "whatsapp" }
    }
  ]
}
```

## 注意事项

1. **Bindings 顺序很重要**：更具体的 binding 应该放在前面
2. **Peer binding 优先级最高**：总是优先于 account 和 channel 级别的 binding
3. **不支持的字段**：
   - ❌ `agents.list[].channels` - 不存在
   - ❌ `channels.telegram.accounts[].agent` - 不存在
   - ✅ 使用 `bindings` 来路由
4. **配置验证**：OpenClaw 启动时会验证配置，错误的字段会导致启动失败
5. **备份配置**：修改配置前总是备份 `openclaw.json`

## 参考文档

完整文档：`~/.nvm/versions/node/v24.14.0/lib/node_modules/openclaw/docs/zh-CN/concepts/multi-agent.md`
