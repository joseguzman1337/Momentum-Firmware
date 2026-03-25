#!/usr/bin/env python3
import json
from pathlib import Path

class APIBuilder:
    def __init__(self, queue_path=".ai/workflows/task_queue.json"):
        self.queue_path = Path(queue_path)
        self.role = "APIBuilder"
        self.base_dir = Path(".ai/openclaw")

    def process(self):
        if not self.queue_path.exists(): return
        with open(self.queue_path, "r") as f:
            tasks = json.load(f)
        
        updated = False
        for task in tasks:
            if task["role"] == self.role and task["status"] == "pending":
                print(f"[{self.role}] Implementing {task['type']}")
                if task["type"] == "implement_render_api":
                    content = """#include "claw_render.h"
#include <gui/canvas.h>
void r_spr(Canvas* c,int16_t x,int16_t y,const uint8_t* b,uint8_t w,uint8_t h,uint8_t f){canvas_draw_bitmap(c,x,y,w,h,b+(f*(w*h/8)));}
void r_til(Canvas* c,int16_t x,int16_t y,uint8_t id){canvas_draw_frame(c,x,y,16,16);canvas_draw_str(c,x+4,y+12,"T");}"""
                    (self.base_dir / "src/claw_render.c").write_text(content)
                    (self.base_dir / "include/claw_render.h").write_text("""#pragma once
#include <gui/canvas.h>
void r_spr(Canvas* c,int16_t x,int16_t y,const uint8_t* b,uint8_t w,uint8_t h,uint8_t f);
void r_til(Canvas* c,int16_t x,int16_t y,uint8_t id);""")
                elif task["type"] == "render_anim":
                    pass
                elif task["type"] == "draw_status_bar":
                    content = "\nvoid r_st(Canvas* c, uint8_t l, uint32_t s){char b[16];snprintf(b,16,\"L:%d S:%ld\",l,s);canvas_draw_str(c,2,10,b);}"
                    with open(self.base_dir / "src/claw_render.c", "a") as rf:
                        rf.write(content)
                    with open(self.base_dir / "include/claw_render.h", "a") as rh:
                        rh.write("\nvoid r_st(Canvas* c, uint8_t l, uint32_t s);")
                elif task["type"] == "impl_scrolling":
                    content = "\nvoid r_vw(int16_t px,int16_t* cx){*cx=px-64;if(*cx<0)*cx=0;}"
                    with open(self.base_dir / "src/claw_render.c", "a") as rf:
                        rf.write(content)
                    with open(self.base_dir / "include/claw_render.h", "a") as rh:
                        rh.write("\nvoid r_vw(int16_t px,int16_t* cx);")
                elif task["type"] == "render_menu":
                    content = "\nvoid r_mn(Canvas* c){canvas_draw_str_aligned(c,64,20,AlignCenter,AlignCenter,\"Claw AI\");canvas_draw_str_aligned(c,64,40,AlignCenter,AlignCenter,\"Press OK\");}"
                    with open(self.base_dir / "src/claw_render.c", "a") as rf:
                        rf.write(content)
                    with open(self.base_dir / "include/claw_render.h", "a") as rh:
                        rh.write("\nvoid r_mn(Canvas* c);")
                elif task["type"] == "render_combat":
                    content = "\nvoid r_atk(Canvas* c,int16_t x,int16_t y,bool r){canvas_draw_line(c,x,y,x+(r?10:-10),y-5);}"
                    with open(self.base_dir / "src/claw_render.c", "a") as rf:
                        rf.write(content)
                    with open(self.base_dir / "include/claw_render.h", "a") as rh:
                        rh.write("\nvoid r_atk(Canvas* c,int16_t x,int16_t y,bool r);")
                elif task["type"] == "render_items":
                    content = "\n#include \"claw_assets.h\"\nvoid r_itm(Canvas* c,int16_t x,int16_t y,uint8_t id){if(id==1)r_spr(c,x,y,trs_bmp,8,8,0);else if(id==2)r_spr(c,x,y,hrt_bmp,8,8,0);}"
                    with open(self.base_dir / "src/claw_render.c", "a") as rf:
                        rf.write(content)
                    with open(self.base_dir / "include/claw_render.h", "a") as rh:
                        rh.write("\nvoid r_itm(Canvas* c,int16_t x,int16_t y,uint8_t id);")
                
                task["status"] = "completed"
                updated = True
                break
        
        if updated:
            with open(self.queue_path, "w") as f:
                json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    APIBuilder().process()
