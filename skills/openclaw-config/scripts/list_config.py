#!/usr/bin/env python3
"""
List all agents and their bindings.

Usage:
    python3 list_config.py [--agents] [--bindings] [--channels]
    
Example:
    python3 list_config.py
    python3 list_config.py --agents
    python3 list_config.py --bindings
"""

import json
import sys
from pathlib import Path

def load_config():
    """Load OpenClaw configuration"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_agents(config):
    """List all agents"""
    agents = config.get('agents', {}).get('list', [])
    
    print("\n📋 Agents:")
    print("=" * 60)
    
    for agent in agents:
        agent_id = agent.get('id')
        name = agent.get('name', agent_id)
        workspace = agent.get('workspace', 'default')
        is_default = agent.get('default', False)
        
        print(f"\n  ID: {agent_id}")
        if name != agent_id:
            print(f"  Name: {name}")
        print(f"  Workspace: {workspace}")
        if is_default:
            print(f"  Default: ✓")

def list_bindings(config):
    """List all bindings"""
    bindings = config.get('bindings', [])
    
    print("\n🔗 Bindings:")
    print("=" * 60)
    
    if not bindings:
        print("\n  No bindings configured")
        return
    
    for i, binding in enumerate(bindings, 1):
        agent_id = binding.get('agentId')
        match = binding.get('match', {})
        channel = match.get('channel')
        account_id = match.get('accountId')
        peer = match.get('peer')
        
        print(f"\n  [{i}] Agent: {agent_id}")
        print(f"      Channel: {channel}")
        print(f"      Account: {account_id}")
        
        if peer:
            peer_kind = peer.get('kind')
            peer_id = peer.get('id')
            print(f"      Peer: {peer_kind} - {peer_id}")

def list_channels(config):
    """List all channel accounts"""
    channels = config.get('channels', {})
    
    print("\n📡 Channels:")
    print("=" * 60)
    
    for channel_name, channel_config in channels.items():
        if not channel_config.get('enabled', True):
            continue
        
        print(f"\n  {channel_name.upper()}:")
        
        accounts = channel_config.get('accounts', {})
        for account_id, account_config in accounts.items():
            name = account_config.get('name', account_id)
            enabled = account_config.get('enabled', True)
            bot_token = account_config.get('botToken', '')
            
            status = "✓" if enabled else "✗"
            print(f"    [{status}] {account_id}")
            if name != account_id:
                print(f"        Name: {name}")
            if bot_token:
                print(f"        Token: {bot_token[:20]}...")

def main():
    show_all = len(sys.argv) == 1
    show_agents = show_all or '--agents' in sys.argv
    show_bindings = show_all or '--bindings' in sys.argv
    show_channels = show_all or '--channels' in sys.argv
    
    config = load_config()
    
    print("\n" + "=" * 60)
    print("  OpenClaw Configuration")
    print("=" * 60)
    
    if show_agents:
        list_agents(config)
    
    if show_bindings:
        list_bindings(config)
    
    if show_channels:
        list_channels(config)
    
    print("\n" + "=" * 60)
    print()

if __name__ == '__main__':
    main()
