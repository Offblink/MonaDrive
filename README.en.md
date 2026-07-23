# MonaDrive

GitHub-driven private cloud drive — sync local folders to your private GitHub repositories.

## Features

- **Auto-install dependencies** — detects missing Python packages on startup and pip-installs them
- **GitHub OAuth login** — one-click browser authorization, no manual token creation
- **Multi-repo sidebar** — create (private/public)/rename/delete repos; hover for actions; ↻ refresh
- **File manager** — built-in sidebar to add/delete/rename files; hover to reveal actions; ↻ refresh
- **Drag & drop** — drop files or folders anywhere on the window to copy into current directory
- **Push/Pull** — Push = local overwrites remote, Pull = remote overwrites local (with timeout)
- **Smart push** — pushes existing local commits even when no new changes are detected
- **Commit rollback** — failed pushes automatically undo the local commit
- **Remote detection** — detects deleted repos and prompts re-initialization
- **Offline tolerant** — browse local files even when remote is unreachable
- **Status display** — shows local commits ahead/behind remote in real time
- **Large file detection** — scans for files >100 MB and warns before push
- **Dark/light themes** — toggle with smooth fade, sidebar adapts to theme
- **Chinese/English** — full bilingual UI with instant language switch
- **Git auto-download** — downloads Portable Git on first launch if not installed
- **System tray resident** — closing the window minimizes to tray; double-click tray icon to restore
- **Single instance** — launching a second instance wakes the existing window instead of spawning a new process
- **Secure token storage** — Windows Credential Manager via keyring, never plaintext

## Install

### Requirements

- Python 3.10+
- Windows 10+
- Git (auto-downloaded on first launch if not installed)

### Run

```bash
python main.py
```

Dependencies are auto-installed on first launch — no need to `pip install` manually.

### Register GitHub OAuth App

1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: `MonaDrive` (or any name)
   - **Homepage URL**: `http://127.0.0.1`
   - **Authorization callback URL**: `http://127.0.0.1/callback`
4. Click **Register application**
5. Generate a **Client Secret**
6. Enter the `Client ID` and `Client Secret` in the MonaDrive login screen

## Usage

1. **Login** — enter your OAuth App credentials, click "Sign in with GitHub"
2. **Select repo** — create a repo from sidebar (+), choose private or public; hover to rename/delete; ↻ to refresh
3. **Choose folder** — select any local directory (even non-empty), click "Initialize"
4. **Sync** — edit files directly in File Explorer → click Push to upload; click Pull to overwrite with remote
5. **Status bar** — shows "N modified" / "N new files" / "ahead by N commits" / "behind by N commits"
6. **Tray background** — the app keeps running in the background after closing; right-click the tray icon to quit

## Tech stack

| Component | Technology |
|-----------|-----------|
| GUI | PyQt6 + QSS |
| Git operations | GitPython |
| GitHub API | PyGithub |
| Token storage | keyring (Windows Credential Manager) |
| Font | Monocraft (pixel monospace) |
| i18n | Custom dictionary-based translation |

## Notes

- Repositories default to **private** (public optional)
- Token scopes: `repo` and `delete_repo` (read/write + delete)
- GitHub file size limit: 100 MB per file; ~5 GB per repo
- Stable internet connection required for sync
- Closing the window minimizes to the system tray; right-click the tray icon and select "Quit" to fully exit
- Edit files directly in File Explorer — changes are detected on next Push
- Initializing does NOT auto-pull from remote; user chooses Push or Pull manually
- Click the avatar/user name to switch repos or return to main

## Credits

- Font [Monocraft](https://github.com/IdreesInc/Monocraft) by IdreesInc — Minecraft-style pixel monospace font

## License

MIT
