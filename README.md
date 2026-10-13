# Film Space Custom

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

A browser port of [film-space](https://github.com/maxprokopp/film-space) (an iPhone/ARKit app) for people without a Mac or an iPhone: block a scene with stand-ins, then walk through it with your phone as the camera. Use the recording as a camera-motion reference for AI video tools (e.g. Seedance), import it into Blender, or drive Blender's camera live.

- **Windows PC**: stage the scene and fly the camera with keyboard + mouse.
- **Android phone** (Chrome + ARCore): walk and turn with the phone, the virtual camera follows (WebXR 6DoF tracking, the ARKit equivalent).
- **Recording**: `.mp4` (or `.webm`) video + `.json` camera track and stand-ins.
- **Blender**: import a recording as an animated camera, or drive the active camera in real time from the phone.

No build, no install: one HTML page (three.js from a CDN) and two Blender scripts, Python standard library only.

## Run (PC)

```bash
python -m http.server 8000
```

Open http://localhost:8000 from this folder.

## Controls

**Edit**: drag = orbit · wheel/pinch = zoom · right drag / two fingers = pan ·
drag a figure = move it · tap empty space = deselect · ↺ ↻ (hold) rotate ·
+ Figure / 🗑 · ▲ ▼ raise/lower framing · 🔒 lock viewpoint · ↩ return to it.

**Camera**: lens 35 → 50 → 75 → 200 mm (full-frame) · Shoulder = camera at 1.5 m in the scene centre ·
● REC / ■ STOP · 🔒 / ↩ as above.
On the PC: click the scene, then WASD move, mouse look, Q/E down/up, Shift faster, Esc releases the mouse.

The stand-in layout lives in the URL (`#...`): copy the link to open the same scene on another device.

## Android phone (handheld camera)

WebXR needs HTTPS or `localhost`. Pick one:

1. **USB (recommended)**: enable USB debugging, run `adb reverse tcp:8000 tcp:8000`, open `http://localhost:8000` on the phone.
2. **Wi-Fi**: on the phone open `chrome://flags/#unsafely-treat-insecure-origin-as-secure`, add `http://<PC-IP>:8000` (IP from `ipconfig`), Relaunch, open that address. Allow Python through the Windows firewall on private networks only.

Press **Camera**: the AR session starts and your steps and phone movements drive the camera. iPhone has no WebXR: use the original app there.

## Blender: import a recording

Each REC downloads `film-space-<date>.mp4` + `film-space-<date>.json` (Chrome may ask to allow multiple downloads).

In Blender (tested on 4.5): Scripting → open `film_space_import.py` → set `PATH` to the `.json` → Run Script. Or:

```bash
blender --python film_space_import.py -- C:\path\film-space-XXXX.json
```

It creates a `FilmSpace` collection with an animated `FilmSpaceCam` (location, rotation, focal length, 36 mm sensor) and `StandIn.NN` figures, at the scene's FPS, and sets the frame range. Replace the stand-ins with your characters.

## Blender live: the phone is Blender's camera

1. Blender → Scripting → open `film_space_live.py` → Run Script. Blender serves the page on port 8001.
2. Phone over USB: `adb reverse tcp:8001 tcp:8001`, open `http://localhost:8001/?blender` in Chrome (or the Wi-Fi route above with port 8001).
3. On the PC look through the camera (Numpad 0). On the phone press **Camera**: Blender's active camera starts from where it is and follows your steps and phone movements. The lens button changes the Blender focal length too.
4. To reposition: move the camera in Blender, then on the phone press Edit and Camera again; Blender re-anchors to the camera's current pose.
5. To record: enable Auto Keying (●) and press Play: the motion becomes keyframes.

Tune at the top of the script: `SCALE` (Blender units per real metre walked) and `SMOOTH` (0 = raw, towards 1 = smoother but more lag).
Without AR (PC, or a phone without ARCore) the same page drives the camera with WASD + mouse.

Notes: the phone shows the simple stand-in scene, not Blender's viewport, so watch the PC monitor. While the script runs, port 8001 is reachable from your local network. The script sets the active camera to quaternion rotation and a 36 mm horizontal sensor.

## Credits

Concept, scene layout, stand-in proportions and camera mapping from [maxprokopp/film-space](https://github.com/maxprokopp/film-space). This is an independent reimplementation for the web.
