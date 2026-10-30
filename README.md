# DriveX

DriveX is an infinite, portrait-view highway driving game written in Python with Pygame CE. The 900 × 1956 logical canvas uses the same tall aspect ratio as an iPhone 16 display (402 × 874 CSS pixels). The web page keeps the game centered and full-height on phones, while desktop browsers get a centered portrait game view. Cars scale into the distance and feature distinct paint colors; sparse traffic waves contain at most two cars and always leave a lane open. Roadside trees, grass, reflectors, and lane markings scroll with the road. Detailed cars, scenery, and sound effects are generated in code; no image or audio assets are needed.

## Controls

- Drag left or right to change lanes.
- Drag up to accelerate; drag down to brake.
- Tap the speaker button in the top-right to mute or enable sound effects.
- Select **Play** to begin; after a crash, choose **Try Again** to restart.
- Keep an eye on the police cruiser closing in behind you.

On desktop, click and hold the mouse button, move, then release to make a swipe. Touch screens use the same drag gestures. Short synthesized sounds play for lane changes, acceleration, braking, restarting, and collisions. On mobile browsers, sound starts after your first gesture so it follows the browser's audio policy.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Async Pygame entry point and responsive display scaling |
| `settings.py` | Logical screen, road, color, and vehicle settings |
| `player.py` | Player car, lane movement, speed, and drawing |
| `traffic.py` | Random traffic spawning, movement, and collision checks |
| `car_drawing.py` | Reusable detailed top-down car illustration |
| `police.py` | Police cruiser pursuit and catch-up behavior |
| `sound_effects.py` | Generated sound effects, with no external audio files |
| `input_handler.py` | Mouse/touch swipe detection and viewport coordinate mapping |
| `game.py` | Game state, road animation, score, and rendering |
| `patch_web.py` | Makes the generated Pygbag page full-height and phone-friendly |

## Run from PyCharm

1. Install Python 3.12 (recommended for the web build) and open this folder as a PyCharm project.
2. In **Settings/Preferences → Project → Python Interpreter**, create or select a project virtual environment using Python 3.12.
3. Open PyCharm's **Terminal** at the project root and install the dependencies:

   ```bash
   python -m pip install pygame-ce pygbag
   ```

4. Run `main.py` from PyCharm. The initial game window uses a phone-shaped portrait layout; resizing fills the new window.

If PyCharm's terminal uses a different interpreter than the project interpreter, select the project virtual environment first or use that interpreter's executable in place of `python`.

## Build the web game

From the project root, run:

```bash
python -m pygbag --build --width 402 --height 874 --ume_block 0 .
python patch_web.py
```

Pygbag writes the static website to **`build/web/`**. That folder contains the web entry page and generated game files; publish its contents, not the Python source folder. The `build/` directory is ignored by Git because the workflow generates it on every deployment.

## Publish on GitHub Pages

This project includes `.github/workflows/pages.yml`. It installs Python 3.12 and the packages in `requirements.txt`, builds the Pygbag game, applies the full-height responsive page layout, and publishes **`build/web/`** as the Pages artifact. It uses an iPhone 16-sized portrait canvas and starts the game without an initial media gate; the Play tap enables browser audio for the synthesized effects and police siren.

1. Create a GitHub repository and push this project to its `main` branch.
2. In the repository, open **Settings → Pages** and set **Build and deployment → Source** to **GitHub Actions**.
3. Open the **Actions** tab. The “Build and deploy DriveX to GitHub Pages” workflow runs on the push; you can also start it with **Run workflow**.
4. When the workflow's build and deploy jobs succeed, open **Settings → Pages** (or the deployment environment in the workflow run) to find the published game URL. The workflow uploads the generated **`build/web/`** folder.

For a GitHub project repository, the URL is normally `https://<your-account>.github.io/<repository-name>/`. The repository must include the workflow file on `main` for automatic deployment.

`pygbag.ini` tells Pygbag to omit local virtual environments and generated/cache folders from the web package.
