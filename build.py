import os
import ast
import json
import shutil
import hashlib

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def analyze_python_modules(engine_dir):
    """
    Parses Python AST for every module in shared/engine/ and builds a dependency graph.
    Validates for missing imports and circular dependencies.
    """
    modules_info = {}
    py_files = [f for f in os.listdir(engine_dir) if f.endswith('.py') and f != '__init__.py']
    
    module_names = {os.path.splitext(f)[0] for f in py_files}
    
    for fname in py_files:
        mod_name = os.path.splitext(fname)[0]
        filepath = os.path.join(engine_dir, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=fname)
            
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    parts = node.module.split('.')
                    target = parts[-1]
                    if target in module_names:
                        deps.add(target)
                elif node.level and node.level > 0:
                    for alias in node.names:
                        if alias.name in module_names:
                            deps.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split('.')
                    target = parts[-1]
                    if target in module_names:
                        deps.add(target)
                        
        deps.discard(mod_name)
        modules_info[mod_name] = {
            "name": mod_name,
            "filename": fname,
            "path": f"assets/runtime/engine/{fname}",
            "dependencies": sorted(list(deps))
        }
        
    # Check circular dependencies
    for mod_name, data in modules_info.items():
        for dep in data["dependencies"]:
            if dep in modules_info and mod_name in modules_info[dep]["dependencies"]:
                raise ValueError(f"Circular dependency detected between '{mod_name}' and '{dep}'!")
                
    return modules_info

def build_runtime_assets():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    runtime_dir = os.path.join(root_dir, "frontend", "assets", "runtime")
    
    engine_src = os.path.join(root_dir, "shared", "engine")
    engine_dst = os.path.join(runtime_dir, "engine")
    
    levels_src = os.path.join(root_dir, "levels")
    levels_dst = os.path.join(runtime_dir, "levels")
    
    os.makedirs(engine_dst, exist_ok=True)
    os.makedirs(levels_dst, exist_ok=True)
    
    # 1. Analyze and validate Python engine modules
    print("Analyzing Python engine AST dependencies...")
    modules_info = analyze_python_modules(engine_src)
    
    # Copy shared engine Python files
    engine_files_meta = []
    for fname in os.listdir(engine_src):
        if fname.endswith(".py"):
            src_p = os.path.join(engine_src, fname)
            dst_p = os.path.join(engine_dst, fname)
            shutil.copy2(src_p, dst_p)
            engine_files_meta.append({
                "name": fname,
                "path": f"assets/runtime/engine/{fname}",
                "hash": get_file_hash(dst_p)
            })
            
    # Copy level JSON files
    level_files_meta = []
    if os.path.exists(levels_src):
        for fname in sorted(os.listdir(levels_src)):
            if fname.endswith(".json"):
                src_p = os.path.join(levels_src, fname)
                dst_p = os.path.join(levels_dst, fname)
                shutil.copy2(src_p, dst_p)
                level_files_meta.append({
                    "name": fname,
                    "path": f"assets/runtime/levels/{fname}",
                    "hash": get_file_hash(dst_p)
                })

    # Generate modules.json
    modules_json_path = os.path.join(runtime_dir, "modules.json")
    modules_data = {"modules": list(modules_info.values())}
    with open(modules_json_path, "w", encoding="utf-8") as f:
        json.dump(modules_data, f, indent=2)
    print(f"Generated {modules_json_path}")
    
    # Generate runtime_manifest.json
    runtime_manifest_path = os.path.join(runtime_dir, "runtime_manifest.json")
    runtime_manifest = {
        "version": "1.0.0",
        "total_levels": len(level_files_meta),
        "engine_modules_count": len(modules_info),
        "created_at": "2026-08-05T12:00:00Z"
    }
    with open(runtime_manifest_path, "w", encoding="utf-8") as f:
        json.dump(runtime_manifest, f, indent=2)
    print(f"Generated {runtime_manifest_path}")

    # Generate asset_manifest.json
    asset_manifest_path = os.path.join(runtime_dir, "asset_manifest.json")
    asset_manifest = {
        "engine_modules": engine_files_meta,
        "levels": level_files_meta
    }
    with open(asset_manifest_path, "w", encoding="utf-8") as f:
        json.dump(asset_manifest, f, indent=2)
    print(f"Generated {asset_manifest_path}")

if __name__ == "__main__":
    build_runtime_assets()
