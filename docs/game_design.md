# Arrow Escape - Game Design Document

## 1. Overview
Arrow Escape is a directional sliding puzzle game. The objective is to clear the board by tapping arrows that have an unblocked path in the direction they are pointing. Removing arrows clears the path for others.

## 2. Aesthetics & Theme
- **Theme**: Minimalist Flat Design (default).
- **Colors**: Deep slate/navy backgrounds (Dark mode by default). Arrows will feature vibrant, distinct colors to allow quick visual parsing.
- **UI Style**: Modern, rounded edges (12px radius), tactile button scaling (0.95x on press) for responsive feedback.

## 3. Screen Specifications

### 3.1 Authentication (Login / Signup / Guest)
- **Visuals**: Animated background featuring floating arrows.
- **Components**:
  - Big bold Logo: "Arrow Escape".
  - Buttons: `Play as Guest`, `Login`, `Sign Up`.
  - Input fields for Email and Password.
- **UX**: Guest mode bypasses authentication entirely and uses local SQLite/storage, which can later be linked to an email.

### 3.2 Home Screen (Main Menu)
- **Top Bar**: User Avatar, Player Name, Current Coins (🟡), Total Stars (⭐).
- **Center**: Large, pulsing `PLAY` button that automatically resumes the highest unlocked level.
- **Bottom Navigation**: Icons linking to `Level Select`, `Shop`, `Leaderboard`, `Achievements`, and `Settings`.

### 3.3 Level Selection
- **Layout**: A pagination or scrolling grid of levels (e.g., 1 to 100).
- **Level Cards**:
  - Number of the level.
  - Up to 3 stars displayed below the number.
  - A padlock icon and grayed-out look for locked levels.

### 3.4 Game Screen (Core Gameplay)
- **Top Bar**: 
  - Left: `Pause` (||)
  - Center: `Level X`
  - Right: `Undo` (↺) and `Hint` (💡)
- **Center Canvas**: The MxN puzzle grid. Arrows are vibrant and distinct from the background.
- **UX Rules**: 
  - Player taps an arrow.
  - If the path is unblocked to the board edge in the arrow's direction, it slides out.
  - If blocked, the arrow shakes and plays an "error/blocked" sound.

### 3.5 Overlays & Menus
- **Pause Menu (Modal)**: Dims the background. Buttons for `Resume`, `Restart Level`, `Sound Toggle`, `Quit to Menu`.
- **Victory Screen (Modal)**: 
  - Dynamic "Level Complete!" text.
  - Star reveal animation (1, 2, or 3 stars based on time/moves).
  - Rewards summary (+50 Coins).
  - Buttons: `Next Level`, `Replay`, `Home`.
- **Hint Confirmation (Modal)**: "Use 1 Hint for 50 Coins?" -> Yes/No. If accepted, the optimal next arrow to tap glows or pulses.

### 3.6 Meta-Game Screens
- **Shop / Theme Store**: Buy aesthetic changes using in-game coins (e.g., Neon Arrows, Wooden Arrows, Minimalist Dark Mode).
- **Leaderboard**: Global ranking tabs (Weekly, All-Time) fetching data from the FastAPI backend.
- **Achievements**: List of badges (e.g., "First Steps: Clear Level 1", "Perfectionist: 3 Stars on 10 Levels"). Locked badges are silhouetted.
- **Profile**: View statistics (Total arrows cleared, time played) and link Guest account to Email.
- **Settings**: Sliders for SFX Volume, Music Volume, and a Dark/Light mode toggle.

## 4. Animations & Effects
- **Slide-Out**: Swift, easing-in acceleration as the arrow leaves the board.
- **Blocked Error**: Rapid horizontal or vertical shake (depending on the arrow's direction).
- **Victory Confetti**: Particle explosion on level completion.
- **Button Press**: Slight scale-down (0.95x) on pointer down/tap to make UI feel tactile.
