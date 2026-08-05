export class PyodideLoader {
    constructor() {
        this.pyodide = null;
        this.engine = null;
    }

    async init() {
        this.pyodide = await loadPyodide();
        
        await this.loadModule('shared/__init__.py', '');
        await this.loadModule('shared/engine/__init__.py', '');
        await this.loadModule('shared/engine/models.py', await this.fetchText('assets/runtime/engine/models.py'));
        await this.loadModule('shared/engine/board.py', await this.fetchText('assets/runtime/engine/board.py'));
        await this.loadModule('shared/engine/events.py', await this.fetchText('assets/runtime/engine/events.py'));
        await this.loadModule('shared/engine/engine.py', await this.fetchText('assets/runtime/engine/engine.py'));
        await this.loadModule('shared/engine/level_parser.py', await this.fetchText('assets/runtime/engine/level_parser.py'));
        await this.loadModule('shared/engine/solver.py', await this.fetchText('assets/runtime/engine/solver.py'));

        await this.pyodide.runPythonAsync(`import sys; sys.path.append('/')`);
    }

    async fetchText(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to fetch ${url}`);
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
        
        // 1. Try REST API endpoint if numeric or valid ID
        try {
            const apiRes = await fetch(`/api/v1/levels/${levelNumOrId}`);
            if (apiRes.ok) {
                const jsonData = await apiRes.json();
                jsonText = JSON.stringify(jsonData);
            }
        } catch (e) {
            console.log(`API fetch skipped for level ${levelNumOrId}, falling back to static runtime asset...`);
        }

        // 2. Fallback to static runtime asset inside frontend/assets/runtime/levels/
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
