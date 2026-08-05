# Arrow Escape Developer Guide — Python Engine Dependency & Build Pipeline

This guide explains how **Arrow Escape** automatically discovers, validates, and loads Python engine modules into the browser using Python AST analysis and Pyodide WebAssembly.

---

## 📌 1. Adding a New Engine Module

When adding a new `.py` file to `shared/engine/` (e.g. `shared/engine/analytics.py` or `shared/engine/ai_solver.py`):

1. **Write your Python code**: Use standard relative (`from .models import Arrow`) or absolute (`from shared.engine.constants import GameState`) imports.
2. **Run `python build.py`**:
   ```bash
   python build.py
   ```
3. **That's it!** The build script will automatically:
   - Parse AST import nodes.
   - Detect dependencies.
   - Verify there are zero circular imports or missing modules.
   - Generate `frontend/assets/runtime/modules.json`, `runtime_manifest.json`, `asset_manifest.json`, and `build_report.json`.
   - Copy the module into `frontend/assets/runtime/engine/`.

> [!NOTE]
> You **never** need to edit `frontend/js/engine/pyodide_loader.js` when adding new engine files. The loader dynamically reads `modules.json` and loads modules in topological dependency order!

---

## 🛠️ 2. Build Pipeline & AST Validation (`build.py`)

`build.py` enforces three build-time validations before generating runtime assets:

1. **Duplicate Module Name Detection**: Fails if two `.py` files share the same module name across subdirectories.
2. **Missing Import Detection**: Fails if a module imports a local module that does not exist in the codebase.
3. **Circular Dependency Detection**: Uses Depth-First Search (DFS) cycle detection. If `A -> B -> A` exists, the build is aborted immediately and logs the exact cycle path:
   ```text
   CIRCULAR DEPENDENCY ERROR: Cycle detected:
     engine.py -> models.py -> engine.py
   ```

---

## 📄 3. Generated Runtime Manifests

- **`modules.json`**: Contains topologically ordered modules, file paths, and dependency IDs for the browser.
- **`runtime_manifest.json`**: Contains build status, versioning, module counts, and total level counts.
- **`asset_manifest.json`**: List of all required engine files, levels, fonts, audio, and images.
- **`build_report.json`**: Diagnostic report detailing build duration, load order, full dependency graph, warnings, and errors.

---

## 🌐 4. Browser Pyodide Loader Flow (`pyodide_loader.js`)

1. **Fetch `modules.json`**: Reads the module manifest.
2. **Topological Sort**: Performs secondary runtime topological resolution.
3. **Module Mounting**: Mounts modules into Pyodide's virtual filesystem (`shared/engine/filename.py`).
4. **Progress Updates**: Sends progressive percentage callbacks to the UI loader overlay (10% $\rightarrow$ 100%).
5. **Memory Caching**: Caches module contents in memory to eliminate duplicate HTTP requests.

---

## 🧪 5. Testing & Verification

Run the automated test suite to ensure 100% test pass rate:
```bash
pytest
```
