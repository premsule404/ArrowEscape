import os
import sys
import json
import time
import subprocess

def run_step(step_name, func):
    print(f"\n[PIPELINE] Running step: {step_name}...")
    t0 = time.time()
    try:
        func()
        dt = time.time() - t0
        print(f"  [OK] {step_name} completed in {dt:.3f}s")
        return True
    except Exception as e:
        print(f"  [ERROR] {step_name} failed: {e}")
        return False

def step_ast_and_manifests():
    root = os.path.dirname(os.path.abspath(__file__))
    build_script = os.path.join(root, "build.py")
    res = subprocess.run([sys.executable, build_script], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"build.py failed:\n{res.stderr}")

def step_validate_pwa():
    root = os.path.dirname(os.path.abspath(__file__))
    manifest_p = os.path.join(root, "frontend", "manifest.json")
    sw_p = os.path.join(root, "frontend", "sw.js")
    
    if not os.path.exists(manifest_p):
        raise FileNotFoundError("frontend/manifest.json is missing.")
    if not os.path.exists(sw_p):
        raise FileNotFoundError("frontend/sw.js is missing.")
        
    with open(manifest_p, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("name") == "Arrow Escape", "Invalid manifest.json name"

def step_validate_electron():
    root = os.path.dirname(os.path.abspath(__file__))
    el_main = os.path.join(root, "electron", "main.js")
    el_pkg = os.path.join(root, "electron", "package.json")
    
    if not os.path.exists(el_main):
        raise FileNotFoundError("electron/main.js is missing.")
    if not os.path.exists(el_pkg):
        raise FileNotFoundError("electron/package.json is missing.")
        
    with open(el_pkg, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "electron" in json.dumps(data), "Invalid electron/package.json"

def main():
    print("=" * 60)
    print("[PACKAGE] Arrow Escape Phase 8: Cross-Platform Packaging Pipeline")
    print("=" * 60)
    
    steps = [
        ("AST Discovery & Engine Manifests", step_ast_and_manifests),
        ("PWA Manifest & Service Worker", step_validate_pwa),
        ("Electron Desktop Configuration", step_validate_electron)
    ]
    
    success_count = 0
    for name, fn in steps:
        if run_step(name, fn):
            success_count += 1
            
    print("\n" + "=" * 60)
    if success_count == len(steps):
        print(f"[SUCCESS] All {len(steps)} packaging targets built & verified!")
    else:
        print(f"[WARNING] Only {success_count}/{len(steps)} steps succeeded.")
    print("=" * 60)

if __name__ == "__main__":
    main()
