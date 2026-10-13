"""Film Space Custom live: drive Blender's active camera from the phone in real time.

Blender > Scripting > open this file > Run Script. Then on the phone open
http://localhost:8001/?blender (with `adb reverse tcp:8001 tcp:8001`) and press Camera.
Every time you enter Camera mode on the phone, the motion is anchored to where the Blender camera is now.
Timeline playing + Auto Keying on = the motion is keyframed. Run the script again to restart.
The phone's 📷 button saves the camera view (as the 3D viewport shows it) to shots/ next to this script.
"""
import bpy, json, math, os, threading, time
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from mathutils import Quaternion, Vector

# folder with index.html = this script's folder (Text editor: the opened file's path)
DIR = os.path.dirname(bpy.path.abspath(next((t.filepath for t in bpy.data.texts if t.filepath.endswith("film_space_live.py")), __file__)))
PORT = 8001
SCALE = 1.0    # Blender units per real metre walked (e.g. 10 to cross a big set)
SMOOTH = 0.35  # 0 = raw tracking, towards 1 = smoother but laggier

Y_TO_Z = Quaternion((1, 0, 0), math.radians(90))  # three.js Y-up -> Blender Z-up
latest = {}  # last pose from the phone, written by the server thread
state = {}   # anchor + smoothed pose, used by the timer on Blender's main thread


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive: one connection for ~60 poses/s

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        code = 204
        if self.path == "/shot":
            latest["shot"] = True
        else:
            try:
                d = json.loads(self.rfile.read(min(n, 4096)))
                p, q = [float(v) for v in d["p"]], [float(v) for v in d["q"]]
                mm = float(d["mm"])
                if len(p) != 3 or len(q) != 4 or not all(map(math.isfinite, p + q + [mm])):
                    raise ValueError
                latest.update(s=str(d["s"])[:32], p=Vector((p[0], -p[2], p[1])),
                              q=Y_TO_Z @ Quaternion((q[3], q[0], q[1], q[2])), mm=min(max(mm, 1), 1000))
            except Exception:
                code = 400
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


def heading(q):
    f = q @ Vector((0, 0, -1))
    return math.atan2(f.y, f.x)


def target_pose(d):
    """Same mapping as applyDevice() in index.html: anchor pose + device motion since anchoring."""
    rot = state["E_q"] @ state["ref_q"].inverted() @ d["q"]
    delta = (d["p"] - state["ref_p"]) * SCALE
    delta.rotate(Quaternion((0, 0, 1), heading(state["E_q"]) - heading(state["ref_q"])))
    return state["E_p"] + delta, rot


def shot():
    """Viewport render of the scene camera: viewport shading if a 3D view looks through the camera, else Solid."""
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=win, area=area, region=region):
        bpy.ops.render.opengl(view_context=area.spaces.active.region_3d.view_perspective == "CAMERA")
    path = os.path.join(DIR, "shots", time.strftime("shot-%Y%m%d-%H%M%S.png"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.data.images["Render Result"].save_render(path)
    print("Film Space Custom screenshot:", path)


def tick():
    scn = bpy.context.scene
    cam = scn.camera
    if latest.pop("shot", None) and cam:
        try:
            shot()
        except Exception as e:  # an exception would unregister the timer and stop live tracking
            print("Film Space Custom screenshot failed:", e)
    if not cam or "s" not in latest:
        return 1 / 60
    d = dict(latest)
    if state.get("s") != d["s"]:  # new Camera session on the phone
        cam.rotation_mode = "QUATERNION"
        state.update(s=d["s"], E_p=cam.location.copy(), E_q=cam.rotation_quaternion.copy(),
                     ref_p=d["p"], ref_q=d["q"], loc=cam.location.copy(), rot=cam.rotation_quaternion.copy())
    loc, rot = target_pose(d)
    state["loc"] = state["loc"].lerp(loc, 1 - SMOOTH)
    state["rot"] = state["rot"].slerp(rot, 1 - SMOOTH)
    cam.location, cam.rotation_quaternion = state["loc"], state["rot"]
    cam.data.sensor_fit, cam.data.sensor_width, cam.data.lens = "HORIZONTAL", 36, d["mm"]
    playing = any(w.screen.is_animation_playing for w in bpy.context.window_manager.windows)
    if playing and scn.tool_settings.use_keyframe_insert_auto:
        cam.keyframe_insert("location")
        cam.keyframe_insert("rotation_quaternion")
        cam.data.keyframe_insert("lens")
    return 1 / 60


ns = bpy.app.driver_namespace
if "film_space_live" in ns:  # re-run: stop the previous server and timer
    old_srv, old_tick = ns.pop("film_space_live")
    old_srv.shutdown()
    old_srv.server_close()
    if bpy.app.timers.is_registered(old_tick):
        bpy.app.timers.unregister(old_tick)
srv = ThreadingHTTPServer(("0.0.0.0", PORT), partial(Handler, directory=DIR))
threading.Thread(target=srv.serve_forever, daemon=True).start()
bpy.app.timers.register(tick, persistent=True)
ns["film_space_live"] = (srv, tick)
print(f"Film Space Custom live on port {PORT}: open http://localhost:{PORT}/?blender on the phone")
