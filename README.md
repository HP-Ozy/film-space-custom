<h1 align="center"><img src="assets/title.webp" alt="Film Space Custom"></h1>

<p>
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0wIDBoMTF2MTFIMHpNMTMgMGgxMXYxMUgxM3pNMCAxM2gxMXYxMUgwek0xMyAxM2gxMXYxMUgxM3oiLz48L3N2Zz4=" alt="Windows">
  <img src="https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/Blender-E87D0D?style=for-the-badge&logo=blender&logoColor=white" alt="Blender">
</p>

**Handheld virtual camera for Windows + Android, with live Blender control.**

<p align="center">
  <img src="assets/workflow-demo.gif" alt="Workflow: stand-ins blocked in the virtual studio, real handheld camera motion, AI style-transfer output" width="400">
  <br>
  <sub>The workflow: block stand-ins in the virtual studio (bottom left), perform the camera move for real with the phone (bottom right), feed the recording to an AI video model for the final look (top).<br>
  Footage from the original <a href="https://github.com/maxprokopp/film-space">film-space</a> iOS demo by maxprokopp; Film Space Custom reproduces the same process on Windows and Android.</sub>
</p>

## Concept

Direct a virtual camera by physically moving your phone. You block a scene with stand-ins, then walk through it holding an Android phone: every step, turn and tilt becomes camera motion, as on a real set. That real, human camera movement drives Blender's camera, live or from a recording, so you can render it with your own characters and environments or use it as a motion reference for AI video tools. It is the [film-space](https://github.com/maxprokopp/film-space) idea (iPhone + ARKit) rebuilt for Windows and Android, with no Mac or iPhone needed.

## What it does

- **Virtual studio** (`index.html`): 20 × 20 m checkerboard floor, 1 m grid, axes and 1.75 m human stand-ins. In **Edit** mode you orbit, zoom and pan the view, add, move, rotate and delete stand-ins, raise or lower the framing, and lock or return to a viewpoint. The layout is saved in the page URL.
- **Camera mode**: on an Android phone (Chrome + ARCore), WebXR tracks the phone in 6DoF, the same kind of tracking as ARKit, and the virtual camera follows it. Real steps become real distances, and turning or tilting the phone aims the camera. On a PC the same mode uses WASD + mouse. Lens: pinch with two fingers (or the mouse wheel) to zoom from 12 to 300 mm, or tap the lens button for 35, 50, 75 and 200 mm (full frame). 📷 takes a screenshot: a PNG on the phone, or with Blender live, the camera view saved by Blender in `shots/`. **Shoulder** places the camera at 1.5 m in the scene centre.
- **Recording**: REC saves the rendered view as `.mp4` plus a `.json` file with the camera track (time, position, rotation, lens) and the stand-in layout.
- **Blender import** (`film_space_import.py`): turns the `.json` into an animated camera (location, rotation and focal length on a 36 mm sensor, at the scene's FPS) plus stand-in figures.
- **Blender live** (`film_space_live.py`): Blender serves the page to the phone and receives its pose about 60 times a second. It applies the pose to the active camera with smoothing, and records keyframes while the timeline plays with Auto Keying on.

## Setup and use with Blender

### Requirements

| | |
|---|---|
| PC | Windows 10/11 with [Blender](https://www.blender.org/download/) 4.5 (tested) and Python 3 for recording mode |
| Phone | Android with Chrome and [Google Play Services for AR](https://play.google.com/store/apps/details?id=com.google.ar.core) (tested on Samsung Galaxy A55, Android 16) |
| Link | USB cable with [adb platform-tools](https://developer.android.com/tools/releases/platform-tools); on the phone, enable Developer options → USB debugging and accept the "Allow USB debugging" prompt |

### Live: the phone is Blender's camera

1. Clone this repo. In Blender go to **Scripting**, open `film_space_live.py` and press **Run Script**. Blender now serves the page on port 8001.
2. Connect the phone over USB and run:
   ```bash
   adb reverse tcp:8001 tcp:8001
   ```
3. On the phone, open `http://localhost:8001/?blender` in Chrome.
4. In Blender, look through the camera (Numpad 0). On the phone, press **Camera**: Blender's active camera starts from its current position and follows your steps and phone movements. Pinch zoom and the lens button also set Blender's focal length; 📷 saves Blender's camera view to `shots/`.
5. To reposition, move the camera in Blender, then on the phone press **Edit** and **Camera** again: the motion re-anchors to the camera's new pose.
6. To record a take, enable **Auto Keying** (●) and press **Play**: the motion is written as keyframes.

Tuning at the top of `film_space_live.py`:
- `SCALE`: Blender units per real metre walked. Use 10 to cross a large set with a few steps.
- `SMOOTH`: 0 gives raw tracking; values closer to 1 are smoother but lag more.

### From a recording

1. Serve the page on the PC with `python -m http.server 8000` in the repo folder.
2. Run `adb reverse tcp:8000 tcp:8000`, then open `http://localhost:8000` on the phone.
3. Block the scene, press **Camera** and record with **● REC**. You get `film-space-<date>.mp4` and `film-space-<date>.json`.
4. In Blender go to **Scripting**, open `film_space_import.py`, set `PATH` to the `.json` and press **Run Script**. You get a `FilmSpace` collection with an animated `FilmSpaceCam` and `StandIn.NN` figures to replace with your characters. From a terminal you can instead run:
   ```bash
   blender --python film_space_import.py -- C:\path\film-space-XXXX.json
   ```

Notes:
- The phone shows the stand-in scene, not Blender's viewport, so watch the PC monitor while you shoot.
- The scripts set the camera to quaternion rotation and a 36 mm horizontal sensor.
- Port 8001 is open on your local network while the live script runs.

## Troubleshooting

| Problem | Fix |
|---|---|
| `adb devices` shows `unauthorized` | Unlock the phone and accept "Allow USB debugging". If no prompt appears, replug the cable or use Developer options → Revoke USB debugging authorisations. |
| The page does not load on the phone | Make sure the Blender script is running, then run `adb reverse tcp:8001 tcp:8001` again (needed after every replug). |
| **Camera** does not start AR | Update Chrome and Google Play Services for AR, and open the page as `http://localhost:...`, not by IP address. |
| The Blender camera does not move | Make sure the scene has an active camera, and press **Camera** on the phone again to re-anchor. |
| Motion is shaky, or laggy | Raise `SMOOTH` if the motion shakes, lower it if it lags, then run the script again. |

## License

Proprietary. Copyright (c) 2026 HP-Ozy. All rights reserved. The source is visible for reference only; any use requires a written licence from HP-Ozy. See [LICENSE](LICENSE).
