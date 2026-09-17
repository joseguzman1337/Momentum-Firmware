# OpenClaw Implementation Tasks

### Task #1: Warp - Asset Management (openclaw_assets.c)
```
Implement asset loading logic for OpenClaw on Flipper Zero.
1. Define structures for Sprite and Tilemap assets.
2. Implement storage_open/read for loading binary assets from /ext/apps/Games/openclaw/.
3. Ensure memory efficiency: use buffered reads and avoid large heap allocations.
4. Implement a simple cache for frequently used tiles.
```

### Task #2: Codex - Physics Engine (openclaw_engine.c)
```
Implement the core physics for a 2D platformer.
1. Define PlayerState (x, y, velocity, is_jumping, is_grounded).
2. Implement gravity and jumping logic.
3. Implement AABB (Axis-Aligned Bounding Box) collision detection against a tilemap.
4. Add a function openclaw_engine_update(float dt) to step the simulation.
```

### Task #3: Claude - Rendering System (openclaw_render.c)
```
Implement the 1-bit rendering system for Flipper Zero.
1. Implement openclaw_render_tilemap() to draw the level grid to the canvas.
2. Implement openclaw_render_player() with basic sprite animation (idle, walk, jump).
3. Handle viewport scrolling (camera following the player).
4. Optimize rendering to stay within Flipper's frame time constraints.
```
