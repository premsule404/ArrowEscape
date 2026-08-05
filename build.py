import os
import shutil

def build_runtime_assets():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    runtime_dir = os.path.join(root_dir, "frontend", "assets", "runtime")
    
    engine_src = os.path.join(root_dir, "shared", "engine")
    engine_dst = os.path.join(runtime_dir, "engine")
    
    levels_src = os.path.join(root_dir, "levels")
    levels_dst = os.path.join(runtime_dir, "levels")
    
    os.makedirs(engine_dst, exist_ok=True)
    os.makedirs(levels_dst, exist_ok=True)
    
    # Copy shared engine Python files
    if os.path.exists(engine_src):
        for fname in os.listdir(engine_src):
            if fname.endswith(".py"):
                shutil.copy2(os.path.join(engine_src, fname), os.path.join(engine_dst, fname))
        print(f"Copied engine files to {engine_dst}")
        
    # Copy level JSON files
    if os.path.exists(levels_src):
        for fname in os.listdir(levels_src):
            if fname.endswith(".json"):
                shutil.copy2(os.path.join(levels_src, fname), os.path.join(levels_dst, fname))
        print(f"Copied level files to {levels_dst}")

if __name__ == "__main__":
    build_runtime_assets()
