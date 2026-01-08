import os

UPSTREAM_BASE = "upstream/flipperzero-firmware"
ROOT_BASE = "."

DIRS_TO_OVERLAY = ["applications", "assets", "documentation", "furi", "lib", "scripts", "site_scons", "targets"]

def create_overlay():
    for d in DIRS_TO_OVERLAY:
        upstream_dir = os.path.join(UPSTREAM_BASE, d)
        root_dir = os.path.join(ROOT_BASE, d)
        
        if not os.path.exists(upstream_dir):
            print(f"Skipping {d}, not in upstream")
            continue
            
        print(f"Overlaying {d}...")
        for dirpath, dirnames, filenames in os.walk(upstream_dir):
            rel_path = os.path.relpath(dirpath, upstream_dir)
            if rel_path == ".":
                target_dir = root_dir
            else:
                target_dir = os.path.join(root_dir, rel_path)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            for filename in filenames:
                if filename.startswith(".git"):
                    continue
                upstream_file = os.path.join(dirpath, filename)
                target_file = os.path.join(target_dir, filename)
                
                if not os.path.exists(target_file) and not os.path.islink(target_file):
                    print(f"Symlinking file: {target_file}")
                    rel_upstream = os.path.relpath(upstream_file, os.path.dirname(target_file))
                    os.symlink(rel_upstream, target_file)

if __name__ == "__main__":
    create_overlay()
