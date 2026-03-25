#!/usr/bin/env python3
import json
from pathlib import Path

class TestRunner:
    def __init__(self, queue_path=".ai/workflows/task_queue.json"):
        self.queue_path = Path(queue_path)
        self.role = "TestRunner"
        self.base_dir = Path(".ai/openclaw")

    def process(self):
        if not self.queue_path.exists(): return
        with open(self.queue_path, "r") as f:
            tasks = json.load(f)
        
        updated = False
        for task in tasks:
            if task["role"] == self.role and task["status"] == "pending":
                print(f"[{self.role}] Implementing {task['type']}")
                if task["type"] == "test_engine_logic":
                    content = """#include "claw_engine.h"
#include <furi.h>
void test_e_upd(){
PSt p={0,0,0,0,0,0};e_upd(&p,1.0f);
if(p.vy>0)FURI_LOG_I("TEST","GPass");
p.y=50;e_upd(&p,1.0f);
if(p.y==48&&p.g)FURI_LOG_I("TEST","CPass");}"""
                    (self.base_dir / "src/test_engine.c").write_text(content)
                elif task["type"] == "audit_memory":
                    content = "\nvoid audit_mem(){FURI_LOG_I(\"MEM\",\"Free:%zu\",memmgr_get_free_heap());}"
                    with open(self.base_dir / "src/test_engine.c", "a") as tf:
                        tf.write(content)
                
                task["status"] = "completed"
                updated = True
                break
        
        if updated:
            with open(self.queue_path, "w") as f:
                json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    TestRunner().process()
