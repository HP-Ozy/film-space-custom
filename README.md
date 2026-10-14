<h1 align="center"><img src="assets/title.png" alt="Film Space Custom"></h1>

<p>
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0wIDBoMTF2MTFIMHpNMTMgMGgxMXYxMUgxM3pNMCAxM2gxMXYxMUgwek0xMyAxM2gxMXYxMUgxM3oiLz48L3N2Zz4=" alt="Windows">
  <img src="https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/Blender-E87D0D?style=for-the-badge&logo=blender&logoColor=white" alt="Blender">
</p>

**Your phone becomes a film camera inside a 3D scene.**

## What it is

In 3D animation the camera usually moves too perfectly, and it looks fake. With Film Space Custom you film the way a camera operator does on a real set: you hold an Android phone and walk, turn and tilt it, and the camera in the 3D scene makes exactly the same movement.

You can use that movement in two ways:

- **In Blender**, the free 3D program: the phone drives Blender's camera, so you film your own characters and sets with a real handheld feel.
- **As a reference for AI video tools**: record the movement in a simple scene, then give the clip to an AI video model to restyle it.

It is a Windows and Android version of [film-space](https://github.com/maxprokopp/film-space), which needs an iPhone and a Mac.

<p align="center">
  <img src="assets/workflow-demo.gif" alt="Grey figures placed in the virtual studio, the camera move filmed with the phone, the final AI-styled clip" width="400">
  <br>
  <sub>Bottom left: grey figures mark where the actors stand. Bottom right: the camera move, filmed by walking with the phone. Top: the clip restyled by an AI video model.<br>
  Footage from the original <a href="https://github.com/maxprokopp/film-space">film-space</a> iOS demo by maxprokopp.</sub>
</p>

## The three parts

| File | What it does |
|---|---|
| `index.html` | The page you open on the phone. A simple virtual studio: a checkerboard floor and grey figures (stand-ins) that show where the actors will be. |
| `film_space_live.py` | Run it inside Blender: the phone moves Blender's camera live, while you watch the result on the PC monitor. |
| `film_space_import.py` | Run it inside Blender to load a movement you recorded earlier on the phone. |

## What you need

| | |
|---|---|
| PC | Windows 10 or 11 with [Blender](https://www.blender.org/download/) 4.5 |
| Phone | Android with Chrome and [Google Play Services for AR](https://play.google.com/store/apps/details?id=com.google.ar.core), the Google app that lets the phone sense its own movement (tested on Samsung Galaxy A55, Android 16) |
| Cable | A USB cable, plus Google's free [platform-tools](https://developer.android.com/tools/releases/platform-tools), which let the PC reach the phone over the cable. On the phone turn on *Developer options → USB debugging* and accept the "Allow USB debugging" message. |

## Way 1: film live in Blender

1. Download this project. In Blender open the **Scripting** tab, open `film_space_live.py` and press **Run Script**.
2. Plug in the phone and run this on the PC, so the phone can reach Blender over the cable:
   ```bash
   adb reverse tcp:8001 tcp:8001
   ```
3. On the phone, open Chrome at `http://localhost:8001/?blender`.
4. In Blender, look through the camera (Numpad 0). On the phone press **Camera**: Blender's camera starts from where it is and follows the phone. Watch the PC monitor while you film: the phone only shows the simple studio, not your Blender scene.
5. To start from another spot, move the camera in Blender, then press **Edit** and **Camera** again on the phone.
6. To save the movement, turn on **Auto Keying** (the ● button in Blender's timeline) and press **Play**: Blender stores the camera position at every frame.

Two settings at the top of `film_space_live.py` (run the script again after changing them):
- `SCALE`: how far the camera moves for each real metre you walk. Use 10 to cross a big set in a few steps.
- `SMOOTH`: 0 follows every tremor of your hand; values closer to 1 move more smoothly but react later.

## Way 2: record on the phone, import later

1. In the project folder, start a small web server on the PC with `python -m http.server 8000` (needs [Python](https://www.python.org/downloads/)).
2. Run `adb reverse tcp:8000 tcp:8000`, then open `http://localhost:8000` in Chrome on the phone.
3. Place the figures, press **Camera** and record with **● REC**. You get a video (`film-space-<date>.mp4`) and the movement (`film-space-<date>.json`).
4. In Blender open `film_space_import.py` in the **Scripting** tab, paste the path of the `.json` file into `PATH` and press **Run Script**. You get the animated camera `FilmSpaceCam` and the grey figures `StandIn.NN`, ready to be replaced by your characters.

## Phone buttons

| Button | What it does |
|---|---|
| **Edit** / **Camera** | Edit: arrange the scene. Camera: film by moving the phone. |
| **+ Figure**, ↺ ↻, 🗑 | Add, turn or delete a grey figure. Drag a figure with your finger to move it. |
| ▲ ▼ | Raise or lower the view. |
| Two fingers / lens button | Zoom: spread or pinch two fingers (12 to 300 mm), or tap the button for 35, 50, 75 and 200 mm. Blender's lens follows. |
| **Shoulder** | Put the camera at shoulder height in the centre of the scene. |
| 🔒 / ↩ | Remember the current viewpoint / go back to it. |
| 📷 | Screenshot. Live with Blender, Blender saves its camera view in the `shots` folder; otherwise the phone saves a picture. |
| **● REC** | Record a video plus the movement file for Way 2. |

The arrangement of the figures is saved in the page address, so you can bookmark it. On a PC the page works too: in Camera mode the keys W A S D and the mouse replace walking.

## Problems

| Problem | Fix |
|---|---|
| `adb devices` says `unauthorized` | Unlock the phone and accept "Allow USB debugging". If no message appears, plug the cable in again. |
| The page does not open on the phone | Check that the Blender script is running, then run the `adb reverse` command again (needed every time you plug the cable in). |
| **Camera** does not start | Update Chrome and Google Play Services for AR, and open the page as `http://localhost:...`. |
| Blender's camera does not move | The Blender scene needs an active camera. Press **Camera** on the phone again. |
| The movement shakes, or lags | Raise `SMOOTH` if it shakes, lower it if it lags. |

While the live script runs, Blender accepts connections on port 8001 from your local network.

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright (c) 2026 HP-Ozy.
