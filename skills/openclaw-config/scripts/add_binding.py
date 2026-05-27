#!/usr/bin/env python3
"""
Add a binding to route messages to a specific agent.

Usage:
    python3 add_binding.py <agent-id> <channel> <account-id> [--peer-kind <kind>] [--peer-id <id>]
    
Example:
    python3 add_binding.py project-manager telegram project-manager
    python3 add_binding.py work whatsapp biz
    python3 add_binding.py family whatsapp personal --peer-kind group --peer-id "120363999@g.us"
"""

import json
import sys
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
    backup_path = config_path.with_suffix('.json.backup-binding')
    if config_path.exists():
        import shutil
        shutil.copy2(config_path, backup_path)
    
    # Save new config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Configuration saved (backup: {backup_path})")

def add_binding(agent_id, channel, account_id, peer_kind=None, peer_id=None):
    """Add a binding to route messages to an agent"""
    
    # Load config
    config = load_config()
    
    # Check if agent exists
    agent_ids = [a['id'] for a in config.get('agents', {}).get('list', [])]
    if agent_id not in agent_ids:
        print(f"✗ Agent '{agent_id}' not found!")
        print(f"  Available agents: {', '.join(agent_ids)}")
        return False
    
    # Create bindings array if it doesn't exist
    if 'bindings' not in config:
        config['bindings'] = []
    
    # Build match object
    match = {
        'channel': channel,
        'accountId': account_id
    }
    
    # Add peer if specified
    if peer_kind and peer_id:
        match['peer'] = {
            'kind': peer_kind,
            'id': peer_id
        }
    
    # Create binding
    binding = {
        'agentId': agent_id,
        'match': match
    }
    
    # Check if binding already exists
    for existing in config['bindings']:
        if existing.get('agentId') == agent_id and existing.get('match') == match:
            print(f"⚠ Binding already exists for {agent_id}")
            return True
    
    # Add binding (more specific bindings should come first)
    # Peer-specific bindings are more specific than account-level
    if peer_kind and peer_id:
        # Insert at the beginning (most specific)
        config['bindings'].insert(0, binding)
    else:
        # Append at the end (less specific)
        config['bindings'].append(binding)
    
    print(f"\n🔗 Adding binding:")
    print(f"   Agent: {agent_id}")
    print(f"   Channel: {channel}")
    print(f"   Account: {account_id}")
    if peer_kind and peer_id:
        print(f"   Peer: {peer_kind} - {peer_id}")
    print()
    
    # Save config
    save_config(config)
    
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 add_binding.py <agent-id> <channel> <account-id> [--peer-kind <kind>] [--peer-id <id>]")
        print("\nExample:")
        print("  python3 add_binding.py project-manager telegram project-manager")
        print("  python3 add_binding.py work whatsapp biz")
        print("  python3 add_binding.py family whatsapp personal --peer-kind group --peer-id '120363999@g.us'")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    channel = sys.argv[2]
    account_id = sys.argv[3]
    
    # Parse optional peer arguments
    peer_kind = None
    peer_id = None
    
    i = 4
    while i < len(sys.argv):
        if sys.argv[i] == '--peer-kind' and i + 1 < len(sys.argv):
            peer_kind = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--peer-id' and i + 1 < len(sys.argv):
            peer_id = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if add_binding(agent_id, channel, account_id, peer_kind, peer_id):
        print("✅ Binding added successfully!")
        print("\nNext steps:")
        print("  1. Restart OpenClaw: openclaw gateway restart")
        print("  2. Test the routing by sending a message")
    else:
        print("\n✗ Failed to add binding")
        sys.exit(1)

if __name__ == '__main__':
    main()
