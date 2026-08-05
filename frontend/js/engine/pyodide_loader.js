export class PyodideLoader {
    constructor() {
        this.pyodide = null;
        this.engine = null;
    }

    topoSortModules(modules) {
        const modMap = new Map();
        modules.forEach(m => modMap.set(m.name, m));
        
        const visited = new Set();
        const tempVisited = new Set();
        const sorted = [];
        
        function visit(name) {
            if (tempVisited.has(name)) {
                throw new Error(`Circular dependency detected in module: ${name}`);
            }
            if (!visited.has(name)) {
                tempVisited.add(name);
                const mod = modMap.get(name);
                if (!mod) {
                    throw new Error(`Missing module declaration for: ${name}`);
                }
                for (const dep of (mod.dependencies || [])) {
                    if (modMap.has(dep)) {
                        visit(dep);
                    } else {
                        throw new Error(`Missing module dependency: '${dep}' required by '${name}'!`);
                    }
                }
                tempVisited.delete(name);
                visited.add(name);
                sorted.push(mod);
            }
        }
        
        modules.forEach(m => {
            if (!visited.has(m.name)) {
                visit(m.name);
            }
        });
        
        return sorted;
    }

    async init() {
        try {
            this.pyodide = await loadPyodide();
            
            await this.loadModule('shared/__init__.py', '');
            await this.loadModule('shared/engine/__init__.py', '');
            
            // 1. Fetch modules.json automatically
            const modulesRes = await fetch('assets/runtime/modules.json');
            if (!modulesRes.ok) {
                throw new Error(`Failed to fetch modules.json (Status: ${modulesRes.status})`);
            }
            const modulesData = await modulesRes.json();
            const rawModules = modulesData.modules || [];
            
            // 2. Perform topological sort for dependency resolution
            const orderedModules = this.topoSortModules(rawModules);
            
            // 3. Load modules in order into Pyodide virtual filesystem
            for (const mod of orderedModules) {
                try {
                    const code = await this.fetchText(mod.path);
                    await this.loadModule(`shared/engine/${mod.filename}`, code);
                } catch (err) {
                    const importers = rawModules
                        .filter(m => (m.dependencies || []).includes(mod.name))
                        .map(m => m.filename)
                        .join(', ');
                    const importedByMsg = importers ? ` (imported by: ${importers})` : '';
                    throw new Error(`Missing module: ${mod.filename}${importedByMsg}. Details: ${err.message}`);
                }
            }

            await this.pyodide.runPythonAsync(`import sys; sys.path.append('/')`);
        } catch (error) {
            console.error("[PyodideLoader] Initialization Error:", error);
            throw error;
        }
    }

    async fetchText(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to fetch ${url} (status: ${res.status})`);
        return await res.text();
    }

    async loadModule(path, code) {
        const parts = path.split('/');
        let currentPath = '';
        for (let i = 0; i < parts.length - 1; i++) {
            currentPath += (currentPath ? '/' : '') + parts[i];
            try { this.pyodide.FS.mkdir(currentPath); } catch(e) {}
        }
        this.pyodide.FS.writeFile(path, code);
    }

    async loadLevel(levelNumOrId) {
        let jsonText = null;
        
        try {
            const apiRes = await fetch(`/api/v1/levels/${levelNumOrId}`);
            if (apiRes.ok) {
                const jsonData = await apiRes.json();
                jsonText = JSON.stringify(jsonData);
            }
        } catch (e) {
            console.log(`API fetch skipped for level ${levelNumOrId}, falling back to static runtime asset...`);
        }

        if (!jsonText) {
            let levelStr = typeof levelNumOrId === 'number' ? String(levelNumOrId).padStart(3, '0') : levelNumOrId;
            if (!levelStr.startsWith('level')) {
                levelStr = `level${levelStr}`;
            }
            jsonText = await this.fetchText(`assets/runtime/levels/${levelStr}.json`);
        }

        this.pyodide.globals.set("level_json_str", jsonText);
        
        await this.pyodide.runPythonAsync(`
import json
from shared.engine.level_parser import LevelParser
level_dict = json.loads(level_json_str)
engine, metadata = LevelParser.load_from_json(level_dict)
        `);
        
        this.engine = this.pyodide.globals.get("engine");
        const meta = this.pyodide.globals.get("metadata");
        
        return meta;
    }
}

export const loader = new PyodideLoader();
