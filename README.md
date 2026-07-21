# Arrow Escape

A professional directional sliding puzzle game, available on Web and Android.

## Concept
Every puzzle contains multiple arrows pointing in four cardinal directions (Up, Down, Left, Right). Each arrow can only move in the direction it points. The objective is to release every arrow from the board by clearing their paths.

## Architecture
This project follows a strict modular architecture to avoid duplicating logic across platforms:
- **Core Engine (Python)**: Contains all the game logic, grid manipulation, and collision detection.
- **Web Frontend (HTML5/Canvas)**: Uses JS/Canvas for rendering and integrates the core engine (e.g. via Pyodide) for immediate offline play.
- **Android App (Kivy)**: A native Python mobile interface utilizing the exact same core engine.
- **Backend API (FastAPI)**: REST endpoints for user authentication, cloud saves, leaderboards, and telemetry.

## Directory Structure
- `/backend`: FastAPI service.
- `/shared`: Core Python game engine and utilities.
- `/frontend`: Web assets and JavaScript.
- `/android`: Kivy application source.
- `/docs`: Architecture, APIs, and design documents.
- `/levels`: JSON definitions of the puzzle layouts.

## Getting Started
Please see the `/docs` folder for detailed setup instructions and architectural guidelines.
