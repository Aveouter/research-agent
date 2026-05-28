#!/usr/bin/env python3
"""
Create a new OpenClaw agent with Telegram bot configuration and automatic binding.

Usage:
    python3 create_agent.py <agent-id> <agent-name> <bot-token> [workspace-path] [telegram-account-id]
    
Example:
    python3 create_agent.py project-manager "项目管理助手" "123456:ABC..." "/path/to/workspace"
"""

import json
import sys
import os
from pathlib import Path

def load_config():
    """Load OpenClaw configuration"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save OpenClaw configuration with backup"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    # Create backup
    backup_path = config_path.with_suffix('.json.backup-agent-creator')
    if config_path.exists():
        import shutil
        shutil.copy2(config_path, backup_path)
    
    # Save new config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Configuration saved (backup: {backup_path})")

def create_agent(agent_id, agent_name, bot_token, workspace_path=None, telegram_account_id=None):
    """Create a new agent with Telegram bot configuration and binding"""
    
    # Default values
    if workspace_path is None:
        workspace_path = str(Path.home() / ".openclaw" / "workspace" / agent_id)
    
    if telegram_account_id is None:
        telegram_account_id = agent_id
    
    # Load config
    config = load_config()
    
    # Check if agent already exists
    existing_agents = [a['id'] for a in config.get('agents', {}).get('list', [])]
    if agent_id in existing_agents:
        print(f"✗ Agent '{agent_id}' already exists!")
        return False
    
    # Check if Telegram account already exists
    existing_accounts = config.get('channels', {}).get('telegram', {}).get('accounts', {}).keys()
    if telegram_account_id in existing_accounts:
        print(f"✗ Telegram account '{telegram_account_id}' already exists!")
        return False
    
    # Add Telegram account
    if 'channels' not in config:
        config['channels'] = {}
    if 'telegram' not in config['channels']:
        config['channels']['telegram'] = {'enabled': True, 'accounts': {}}
    if 'accounts' not in config['channels']['telegram']:
        config['channels']['telegram']['accounts'] = {}
    
    config['channels']['telegram']['accounts'][telegram_account_id] = {
        'name': agent_name,
        'enabled': True,
        'dmPolicy': 'pairing',
        'botToken': bot_token,
        'groupPolicy': 'allowlist',
        'streaming': 'off'
    }
    
    print(f"✓ Added Telegram account: {telegram_account_id}")
    
    # Add agent
    if 'agents' not in config:
        config['agents'] = {'list': []}
    if 'list' not in config['agents']:
        config['agents']['list'] = []
    
    new_agent = {
        'id': agent_id,
        'name': agent_name,
        'workspace': workspace_path
    }
    
    config['agents']['list'].append(new_agent)
    
    print(f"✓ Added agent: {agent_id}")
    print(f"  Name: {agent_name}")
    print(f"  Workspace: {workspace_path}")
    
    # Add binding (automatic routing)
    if 'bindings' not in config:
        config['bindings'] = []
    
    binding = {
        'agentId': agent_id,
        'match': {
            'channel': 'telegram',
            'accountId': telegram_account_id
        }
    }
    
    config['bindings'].append(binding)
    
    print(f"✓ Added binding: {telegram_account_id} → {agent_id}")
    
    # Save config
    save_config(config)
    
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 create_agent.py <agent-id> <agent-name> <bot-token> [workspace-path] [telegram-account-id]")
        print("\nExample:")
        print('  python3 create_agent.py project-manager "项目管理助手" "123456:ABC..." "/path/to/workspace"')
        sys.exit(1)
    
    agent_id = sys.argv[1]
    agent_name = sys.argv[2]
    bot_token = sys.argv[3]
    workspace_path = sys.argv[4] if len(sys.argv) > 4 else None
    telegram_account_id = sys.argv[5] if len(sys.argv) > 5 else None
    
    print(f"\n🤖 Creating agent: {agent_id}")
    print(f"   Name: {agent_name}")
    print(f"   Bot token: {bot_token[:20]}...")
    print()
    
    if create_agent(agent_id, agent_name, bot_token, workspace_path, telegram_account_id):
        workspace = workspace_path or Path.home() / '.openclaw' / 'workspace' / agent_id
        print("\n✅ Agent created successfully!")
        print("\nNext steps:")
        print(f"1. Create workspace directory: mkdir -p {workspace}")
        print(f"2. Add configuration files (SOUL.md, AGENTS.md, USER.md)")
        print("   Use templates in assets/ directory")
        print("3. Restart OpenClaw: openclaw gateway restart")
        print("4. Start chatting with your new bot on Telegram!")
    else:
        print("\n✗ Failed to create agent")
        sys.exit(1)

if __name__ == '__main__':
    main()
