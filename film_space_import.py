"""Import a Film Space Web recording (.json) into Blender: animated camera + stand-ins.

Blender > Scripting > open this file > set PATH > Run Script
or: blender --python film_space_import.py -- C:\\path\\film-space-XXXX.json
"""
import bpy, json, math, sys
from mathutils import Quaternion, Vector

PATH = r""  # the .json downloaded next to the video

# three.js is Y-up, Blender is Z-up: (x, y, z) -> (x, -z, y), i.e. +90 deg about X
Y_TO_Z = Quaternion((1, 0, 0), math.radians(90))
def pos(x, y, z): return Vector((x, -z, y))

# same stand-in as the web page (HumanFigureFactory.swift): [w,h,d, x,y,z, rotZ, skin], w=0 is the head
PARTS = [[0,0,0, 0,1.62,0, 0,1], [.36,.48,.18, 0,1.22,0, 0,0],
  [.11,.38,.11, -.24,1.28,0, .35,0], [.11,.38,.11, .24,1.28,0, -.35,0],
  [.09,.34,.09, -.38,1.08,0, .15,1], [.09,.34,.09, .38,1.08,0, -.15,1],
  [.13,.82,.13, -.11,.58,0, 0,0], [.13,.82,.13, .11,.58,0, 0,0],
  [.14,.08,.24, -.11,.04,.02, 0,1], [.14,.08,.24, .11,.04,.02, 0,1]]


def stand_in(i, x, z, ry, col):
    root = bpy.data.objects.new(f"StandIn.{i:02d}", None)
    col.objects.link(root)
    root.location = (x, -z, 0)
    root.rotation_euler = (0, 0, ry)
    for w, h, d, px, py, pz, rz, _ in PARTS:
        if w:
            bpy.ops.mesh.primitive_cube_add(size=1, location=pos(px, py, pz), rotation=(0, -rz, 0), scale=(w, d, h))
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=.11, location=pos(px, py, pz))
        part = bpy.context.active_object
        for c in part.users_collection: c.objects.unlink(part)
        col.objects.link(part)
        part.parent = root


def main(path):
    data = json.load(open(path))
    frames = data["frames"]
    if not frames:
        raise ValueError("no camera frames in " + path)
    scn = bpy.context.scene
    fps = scn.render.fps / scn.render.fps_base
    col = bpy.data.collections.new("FilmSpace")
    scn.collection.children.link(col)

    cam_data = bpy.data.cameras.new("FilmSpaceCam")
    cam_data.sensor_fit = 'HORIZONTAL'
    cam_data.sensor_width = 36  # lens presets are full-frame mm, as in the app
    cam = bpy.data.objects.new("FilmSpaceCam", cam_data)
    col.objects.link(cam)
    cam.rotation_mode = 'QUATERNION'
    scn.camera = cam

    prev = None
    for t, px, py, pz, qx, qy, qz, qw, mm in frames:
        f = 1 + t * fps
        q = Y_TO_Z @ Quaternion((qw, qx, qy, qz))
        if prev is not None and prev.dot(q) < 0:
            q.negate()  # keep sign continuous or Blender interpolates the long way round
        prev = q
        cam.location = pos(px, py, pz)
        cam.rotation_quaternion = q
        cam_data.lens = mm
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
        cam_data.keyframe_insert("lens", frame=f)

    for i, (x, z, ry) in enumerate(data["humans"]):
        stand_in(i, x, z, ry, col)

    scn.frame_start = 1
    scn.frame_end = max(1, round(1 + frames[-1][0] * fps))
    print(f"Film Space: {len(frames)} camera samples, {len(data['humans'])} stand-ins, frames 1-{scn.frame_end}")


main(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else PATH)
