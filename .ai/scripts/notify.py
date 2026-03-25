#!/usr/bin/env python3
"""
Notification handler for Codex automation events in Momentum Firmware
Logs events and sends notifications for AI pipeline monitoring
"""

import json
import sys
import os
import datetime
from pathlib import Path

def log_event(event_data):
    """Log event to automation log file"""
    log_dir = Path("logs/codex")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().isoformat()
    log_file = log_dir / f"notifications_{datetime.date.today().strftime('%Y%m%d')}.log"
    
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {json.dumps(event_data)}\n")

def handle_agent_turn_complete(event_data):
    """Handle agent turn completion events"""
    thread_id = event_data.get("thread-id", "unknown")
    last_message = event_data.get("last-assistant-message", "Turn Complete")
    input_messages = event_data.get("input-messages", [])
    
    # Log the completion
    print(f"Codex Agent Turn Complete - Thread: {thread_id}")
    print(f"Last Message: {last_message}")
    
    # For YOLO mode, just log without interrupting
    if os.getenv("YOLO_MODE") == "true":
        return
    
    # Could add desktop notifications here if needed
    # subprocess.run(["osascript", "-e", f'display notification "{last_message}" with title "Codex Automation"'])

def main():
    if len(sys.argv) < 2:
        print("Usage: notify.py <event_json>")
        return 1
    
    try:
        event_data = json.loads(sys.argv[1])
        log_event(event_data)
        
        event_type = event_data.get("type")
        
        if event_type == "agent-turn-complete":
            handle_agent_turn_complete(event_data)
        else:
            print(f"Unknown event type: {event_type}")
            
    except json.JSONDecodeError as e:
        print(f"Failed to parse event JSON: {e}")
        return 1
    except Exception as e:
        print(f"Error handling notification: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())