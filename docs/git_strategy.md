# Git Strategy & Workflow

## Branching Model
We use a simplified GitFlow model.

- **`main`**: The single source of truth for production-ready code. Commits here must be tagged with a version number for releases.
- **`develop`** (Optional): If the team grows, an active integration branch. Otherwise, feature branches merge directly to `main` via PRs.
- **Feature Branches**: `feature/<feature-name>` (e.g., `feature/level-parser`)
- **Bug Fix Branches**: `bugfix/<issue-name>` (e.g., `bugfix/auth-token-refresh`)

## Commit Messages
We follow **Conventional Commits**:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation updates
- `style:` for formatting, missing semi-colons, etc (no code changes)
- `refactor:` for code refactoring
- `test:` for adding or fixing tests
- `chore:` for updating build tasks, package manager configs, etc.

*Example:* `feat: implement depth-first search for hint generation`
