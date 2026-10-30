# DriveX

DriveX is an infinite, portrait-view highway driving game written in Python with Pygame CE. It uses only Pygame drawing primitives, so there are no image or sound assets to download. The logical game view is 400 × 600 and is scaled proportionally to fit the resizable window or browser canvas.

## Controls

- Drag left or right to change lanes.
- Drag up to accelerate; drag down to brake.
- After a collision, tap or click anywhere to restart.

On desktop, click and hold the mouse button, move, then release to make a swipe. Touch screens use the same drag gestures.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Async Pygame entry point and responsive display scaling |
| `settings.py` | Logical screen, road, color, and vehicle settings |
| `player.py` | Player car, lane movement, speed, and drawing |
| `traffic.py` | Random traffic spawning, movement, and collision checks |
| `input_handler.py` | Mouse/touch swipe detection and viewport coordinate mapping |
| `game.py` | Game state, road animation, score, and rendering |

## Run from PyCharm

1. Install Python 3.12 (recommended for the web build) and open this folder as a PyCharm project.
2. In **Settings/Preferences → Project → Python Interpreter**, create or select a project virtual environment using Python 3.12.
3. Open PyCharm's **Terminal** at the project root and install the dependencies:

   ```bash
   python -m pip install pygame-ce pygbag
   ```

4. Run `main.py` from PyCharm. The window can be resized; the game remains portrait-shaped and centered with letterboxing when needed.

If PyCharm's terminal uses a different interpreter than the project interpreter, select the project virtual environment first or use that interpreter's executable in place of `python`.

## Build the web game

From the project root, run:

```bash
python -m pygbag --build --width 400 --height 600 --ume_block 0 .
```

Pygbag writes the static website to **`build/web/`**. That folder contains the web entry page and generated game files; publish its contents, not the Python source folder. The `build/` directory is ignored by Git because the workflow generates it on every deployment.

## Publish on GitHub Pages

This project includes `.github/workflows/pages.yml`. It installs Python 3.12 and the packages in `requirements.txt`, runs the same Pygbag build command, and publishes **`build/web/`** as the Pages artifact. The build sets the browser canvas to the game's portrait dimensions and disables Pygbag's user-media engagement gate (this game does not use audio or other media).

1. Create a GitHub repository and push this project to its `main` branch.
2. In the repository, open **Settings → Pages** and set **Build and deployment → Source** to **GitHub Actions**.
3. Open the **Actions** tab. The “Build and deploy DriveX to GitHub Pages” workflow runs on the push; you can also start it with **Run workflow**.
4. When the workflow's build and deploy jobs succeed, open **Settings → Pages** (or the deployment environment in the workflow run) to find the published game URL. The workflow uploads the generated **`build/web/`** folder.

For a GitHub project repository, the URL is normally `https://<your-account>.github.io/<repository-name>/`. The repository must include the workflow file on `main` for automatic deployment.

`pygbag.ini` tells Pygbag to omit local virtual environments and generated/cache folders from the web package.
