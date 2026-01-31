#!/usr/bin/env python3
import json
from pathlib import Path

class DataIngestor:
    def __init__(self, queue_path=".ai/workflows/task_queue.json"):
        self.queue_path = Path(queue_path)
        self.role = "DataIngestor"
        self.base_dir = Path(".ai/openclaw")

    def process(self):
        if not self.queue_path.exists(): return
        with open(self.queue_path, "r") as f:
            tasks = json.load(f)
        
        updated = False
        for task in tasks:
            if task["role"] == self.role and task["status"] == "pending":
                print(f"[{self.role}] Processing {task['type']}")
                if task["type"] == "parse_rez_header":
                    # ... existing logic ...
                    content = """#include "claw_assets.h"
#include <storage/storage.h>
typedef struct{char m[8];uint32_t o,s;}RZ;
bool load_rz(const char* p){
Storage* s=furi_record_open(RECORD_STORAGE);File* f=storage_file_alloc(s);bool r=0;
if(storage_file_open(f,p,FSAM_READ,FSOM_OPEN_EXISTING)){RZ h;if(storage_file_read(f,&h,12)==12)r=!strncmp(h.m,"Monolith",8);}
storage_file_free(f);furi_record_close(RECORD_STORAGE);return r;}"""
                    (self.base_dir / "src/claw_assets.c").write_text(content)
                    (self.base_dir / "include/claw_assets.h").write_text("#pragma once\n#include <stdbool.h>\n#include <stdint.h>\nbool load_rz(const char* p);\nuint8_t get_lvl(uint16_t x,uint16_t y);")
                elif task["type"] == "generate_dummy_level":
                    content = "\nuint8_t get_lvl(uint16_t x,uint16_t y){return (y>40)?1:0;}"
                    with open(self.base_dir / "src/claw_assets.c", "a") as af:
                        af.write(content)
                elif task["type"] == "add_cat_bitmap":
                    content = "\nconst uint8_t cat_bmp[]={0x3C,0x42,0xA5,0x81,0xA5,0x99,0x42,0x3C};"
                    with open(self.base_dir / "src/claw_assets.c", "a") as af:
                        af.write(content)
                    with open(self.base_dir / "include/claw_assets.h", "a") as ah:
                        ah.write("\nextern const uint8_t cat_bmp[];")
                elif task["type"] == "expand_level_map":
                    # ... existing logic ...
                    pass
                elif task["type"] == "add_hazards":
                    # ... existing logic ...
                    pass
                elif task["type"] == "add_enemy_bmp":
                    # ... existing logic ...
                    pass
                elif task["type"] == "add_item_bmps":
                    # ... existing logic ...
                    pass
                elif task["type"] == "set_item_coords":
                    content = "\nuint8_t get_itm(uint16_t x){if(x==100)return 1;if(x==180)return 2;return 0;}"
                    with open(self.base_dir / "src/claw_assets.c", "a") as af:
                        af.write(content)
                    with open(self.base_dir / "include/claw_assets.h", "a") as ah:
                        ah.write("\nuint8_t get_itm(uint16_t x);")
                
                task["status"] = "completed"
                updated = True
                break
        
        if updated:
            with open(self.queue_path, "w") as f:
                json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    DataIngestor().process()
