import os
import ast
import json
import shutil
import hashlib
import time

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def scan_python_files(engine_dir):
    """Recursively scan engine_dir for .py files, ignoring __pycache__, tests, and temp files."""
    py_files = []
    for root, dirs, files in os.walk(engine_dir):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'tests', '.pytest_cache', '.git')]
        for f in files:
            if f.endswith('.py') and not f.startswith('.') and f != 'setup.py':
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, engine_dir).replace('\\', '/')
                py_files.append((f, rel_path, full_path))
    return py_files

def find_cycle(graph):
    """DFS Cycle detection returning exact cycle path list if cycle exists."""
    visited = set()
    rec_stack = []
    
    def dfs(node):
        visited.add(node)
        rec_stack.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle: return cycle
            elif neighbor in rec_stack:
                cycle_start_idx = rec_stack.index(neighbor)
                return rec_stack[cycle_start_idx:] + [neighbor]
                
        rec_stack.pop()
        return None

    for node in graph:
        if node not in visited:
            cycle = dfs(node)
            if cycle: return cycle
    return None

def analyze_and_validate_modules(engine_dir):
    py_files = scan_python_files(engine_dir)
    
    # 1. Duplicate Module Name Detection
    mod_name_to_paths = {}
    for fname, rel_path, full_path in py_files:
        mod_name = os.path.splitext(fname)[0]
        if mod_name == '__init__':
            continue
        if mod_name in mod_name_to_paths:
            raise ValueError(f"DUPLICATE MODULE ERROR: Module '{mod_name}' exists in multiple locations: '{mod_name_to_paths[mod_name]}' and '{rel_path}'. Please rename one.")
        mod_name_to_paths[mod_name] = rel_path
        
    known_modules = set(mod_name_to_paths.keys())
    modules_info = {}
    graph = {}
    
    # 2. AST Parsing and Import Extraction
    for fname, rel_path, full_path in py_files:
        mod_name = os.path.splitext(fname)[0]
        if mod_name == '__init__':
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=fname)
            
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    parts = node.module.split('.')
                    target = parts[-1]
                    if target in known_modules:
                        deps.add(target)
                elif node.level and node.level > 0:
                    for alias in node.names:
                        if alias.name in known_modules:
                            deps.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split('.')
                    target = parts[-1]
                    if target in known_modules:
                        deps.add(target)
                        
        deps.discard(mod_name)
        sorted_deps = sorted(list(deps))
        
        modules_info[mod_name] = {
            "id": mod_name,
            "filename": fname,
            "path": f"assets/runtime/engine/{rel_path}",
            "dependencies": sorted_deps
        }
        graph[mod_name] = sorted_deps

    # 3. Circular Dependency Detection
    cycle = find_cycle(graph)
    if cycle:
        cycle_str = " -> ".join(cycle)
        raise ValueError(f"CIRCULAR DEPENDENCY ERROR: Cycle detected:\n  {cycle_str}\nPlease refactor to eliminate circular imports.")

    # 4. Topological Sort
    sorted_modules = []
    visited_sort = set()
    temp_sort = set()
    
    def visit(node):
        if node in temp_sort:
            raise ValueError(f"Circular dependency involving '{node}'")
        if node not in visited_sort:
            temp_sort.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            temp_sort.remove(node)
            visited_sort.add(node)
            sorted_modules.append(modules_info[node])
            
    for mname in sorted(list(modules_info.keys())):
        if mname not in visited_sort:
            visit(mname)
            
    return sorted_modules, modules_info, graph

def build_runtime_assets():
    start_time = time.time()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    runtime_dir = os.path.join(root_dir, "frontend", "assets", "runtime")
    
    engine_src = os.path.join(root_dir, "shared", "engine")
    engine_dst = os.path.join(runtime_dir, "engine")
    levels_src = os.path.join(root_dir, "levels")
    levels_dst = os.path.join(runtime_dir, "levels")
    
    os.makedirs(engine_dst, exist_ok=True)
    os.makedirs(levels_dst, exist_ok=True)
    
    print("=" * 60)
    print("[BUILD] Arrow Escape Phase 3 Pipeline: AST Discovery & Manifests")
    print("=" * 60)
    
    # 1. AST Analysis, Cycle Detection & Topological Sort
    print("[AST] Scanning shared/engine/ for Python modules...")
    sorted_modules, modules_info, dep_graph = analyze_and_validate_modules(engine_src)
    print(f"[OK] Discovered and validated {len(sorted_modules)} Python engine modules cleanly.")
    
    # 2. Copy Engine Files
    engine_files_meta = []
    py_files = scan_python_files(engine_src)
    for fname, rel_path, full_path in py_files:
        dst_p = os.path.join(engine_dst, rel_path)
        os.makedirs(os.path.dirname(dst_p), exist_ok=True)
        shutil.copy2(full_path, dst_p)
        file_hash = get_file_hash(dst_p)
        engine_files_meta.append({
            "filename": fname,
            "path": f"assets/runtime/engine/{rel_path}",
            "hash": file_hash
        })
        print(f"  [OK] Copied engine file: {rel_path}")
        
    # 3. Copy Level Files
    level_files_meta = []
    if os.path.exists(levels_src):
        for fname in sorted(os.listdir(levels_src)):
            if fname.endswith(".json"):
                src_p = os.path.join(levels_src, fname)
                dst_p = os.path.join(levels_dst, fname)
                shutil.copy2(src_p, dst_p)
                file_hash = get_file_hash(dst_p)
                level_files_meta.append({
                    "id": os.path.splitext(fname)[0],
                    "filename": fname,
                    "path": f"assets/runtime/levels/{fname}",
                    "hash": file_hash
                })
        print(f"[OK] Copied {len(level_files_meta)} level JSON layouts.")

    # 4. Generate modules.json (Topologically Sorted)
    modules_json_path = os.path.join(runtime_dir, "modules.json")
    with open(modules_json_path, "w", encoding="utf-8") as f:
        json.dump({"modules": sorted_modules}, f, indent=2)
    print(f"[OK] Generated {modules_json_path}")
    
    # 5. Generate runtime_manifest.json
    runtime_manifest_path = os.path.join(runtime_dir, "runtime_manifest.json")
    runtime_manifest = {
        "version": "1.0.0",
        "total_levels": len(level_files_meta),
        "engine_modules_count": len(sorted_modules),
        "build_status": "SUCCESS",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(runtime_manifest_path, "w", encoding="utf-8") as f:
        json.dump(runtime_manifest, f, indent=2)
    print(f"[OK] Generated {runtime_manifest_path}")

    # 6. Generate asset_manifest.json
    asset_manifest_path = os.path.join(runtime_dir, "asset_manifest.json")
    asset_manifest = {
        "engine_modules": engine_files_meta,
        "levels": level_files_meta,
        "images": [],
        "fonts": ["https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap"],
        "audio": []
    }
    with open(asset_manifest_path, "w", encoding="utf-8") as f:
        json.dump(asset_manifest, f, indent=2)
    print(f"[OK] Generated {asset_manifest_path}")

    # 7. Generate build_report.json
    duration = time.time() - start_time
    build_report_path = os.path.join(runtime_dir, "build_report.json")
    build_report = {
        "status": "SUCCESS",
        "build_time_seconds": round(duration, 4),
        "total_modules": len(sorted_modules),
        "total_levels": len(level_files_meta),
        "load_order": [m["id"] for m in sorted_modules],
        "dependency_graph": dep_graph,
        "warnings": [],
        "errors": []
    }
    with open(build_report_path, "w", encoding="utf-8") as f:
        json.dump(build_report, f, indent=2)
    print(f"[OK] Generated {build_report_path}")
    print("=" * 60)
    print(f"[SUCCESS] Build Completed in {duration:.3f} seconds!")
    print("=" * 60)

if __name__ == "__main__":
    build_runtime_assets()
