# Arrow Escape Architecture

## Core Philosophy
- **Zero Duplication**: The core puzzle mechanics (movement, collision, validation, win states) are written in **one place only** (`/shared/engine`).
- **Separation of Concerns**: The engine does not know how it is being rendered (Canvas vs Kivy) nor does it know about the database.

## System Components

### 1. The Core Engine (`/shared/engine`)
- **Language**: Python
- **Responsibilities**: 
  - Manage the Grid (MxN).
  - Track arrow entities (x, y, direction).
  - Handle sliding logic and boundary detection.
  - Return state transitions to the caller.
  
### 2. Backend Service (`/backend`)
- **Framework**: FastAPI
- **Responsibilities**:
  - Stateless REST APIs.
  - JWT Authentication.
  - CRUD operations for User Profiles, Progress, and Settings.
  - Fetching level data.

### 3. Web Frontend (`/frontend`)
- **Framework**: HTML5 Canvas, Vanilla JS (or lightweight framework like Vite/React if needed later).
- **Responsibilities**:
  - Render the game grid and animate the arrows.
  - Capture mouse/touch events.
  - Load the Python Core Engine in the browser using **Pyodide** (or communicate via lightweight API if Pyodide proves too heavy for mobile web).

### 4. Android Client (`/android`)
- **Framework**: Kivy (Python)
- **Responsibilities**:
  - Native Android UI and rendering.
  - Uses the Core Engine directly since it's also Python.
  - Makes API calls to the Backend for sync.

## Database Schema (SQLAlchemy)
Refer to the upcoming Phase 7 documentation for full schemas. The primary relations will center around `User` -> `Progress` -> `Level`.
