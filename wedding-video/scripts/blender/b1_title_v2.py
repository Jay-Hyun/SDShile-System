"""B1 v2 — title insert in the film's ink-and-ivory look: black lacquer gothic "반대" (groom) and white
porcelain myeongjo "끌림" (bride) drift toward each other and touch gently on the sung 함께.

Only the moving part is rendered; the held tail is the last frame as a still, and the slow push-in is
done in the DOM on top. Timing from insert start (104 BPM, beat 0.577 s):
  0.00 - 2.31  drift together (sine in-out), each turns from a 3/4 view to face camera
  2.31         contact
  2.31 - 2.85  settle (a 3 % nudge back and rest)
blender -b -P scripts/blender/b1_title_v2.py -- --out renders/blender/b1/ --res 1920x1080 --samples 10
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bpy  # noqa: E402
from common import (BEAT, args, area_light, assign, camera, frame, key, reflection_cards,  # noqa: E402
                    reset_scene, set_easing, setup_render, srgb, text_mesh, world_studio)

a = args()
res = tuple(int(v) for v in a.get("res", "1920x1080").split("x"))
out = a.get("out", "renders/blender/b1/")
os.makedirs(out, exist_ok=True)

scene = reset_scene()
setup_render(scene, res=res, samples=int(a.get("samples", 10)), out=os.path.join(out, "f_"))
world_studio(scene, top="#FFF9F0", bottom="#CFC6B8", strength=0.22)

# warm soft key from upper left, long strip highlights for the lacquer, faint cool fill
area_light("key", (-6.5, -5, 5), (55, 0, -50), (4, 4), 1300, "#FFEBD2")
area_light("fill", (6, -5, 1.5), (78, 0, 55), (5, 5), 60, "#E8ECFF")
area_light("rim", (0, 6, 4.5), (-60, 0, 180), (12, 1.0), 900, "#FFFFFF")
reflection_cards(strength=1.6, color="#FFF6EA")

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -1.35))
bpy.context.active_object.is_shadow_catcher = True


def lacquer():
    m = bpy.data.materials.new("lacquer")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb("#0D0C0B")
    p.inputs["Roughness"].default_value = 0.22
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.03
    return m


def porcelain():
    m = bpy.data.materials.new("porcelain")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb("#F6F3EE")
    p.inputs["Roughness"].default_value = 0.38
    p.inputs["Subsurface Weight"].default_value = 0.25
    p.inputs["Subsurface Radius"].default_value = (0.5, 0.4, 0.3)
    p.inputs["Coat Weight"].default_value = 0.7
    p.inputs["Coat Roughness"].default_value = 0.05
    return m


A = text_mesh("반대", "Pretendard-Black.ttf", size=2.05, extrude=0.26, bevel=0.025, bevel_res=3, name="A")
assign(A, lacquer())
B = text_mesh("끌림", "Pretendard-Black.ttf", size=2.05, extrude=0.26, bevel=0.025, bevel_res=3, name="B")
assign(B, porcelain())


def pivot(name, obj, loc):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    obj.parent = e
    obj.location = (0, 0, 0)
    return e


gap = 0.16
lockA = (-(A.dimensions.x / 2 + gap / 2), 0, 0)
lockB = ((B.dimensions.x / 2 + gap / 2), 0, 0)
PA = pivot("PA", A, lockA)
PB = pivot("PB", B, lockB)

r = math.radians
f0, f_hit = frame(0), frame(4 * BEAT)
f_rest = f_hit + 16
key(PA, f0, location=(lockA[0] - 3.4, 0.6, 0.15), rotation_euler=(0, r(-38), r(10)))
key(PB, f0, location=(lockB[0] + 3.4, 0.5, -0.1), rotation_euler=(0, r(40), r(-8)))
key(PA, f_hit, location=lockA, rotation_euler=(0, r(-2), 0))
key(PB, f_hit, location=lockB, rotation_euler=(0, r(2), 0))
for o in (PA, PB):
    set_easing(o, f0, "EASE_IN_OUT", "SINE")
key(PA, f_hit + 6, location=(lockA[0] - 0.05, 0, 0), rotation_euler=(0, r(1), 0))
key(PB, f_hit + 6, location=(lockB[0] + 0.05, 0, 0), rotation_euler=(0, r(-1), 0))
key(PA, f_rest, location=lockA, rotation_euler=(0, 0, 0))
key(PB, f_rest, location=lockB, rotation_euler=(0, 0, 0))

cam = camera(loc=(0, -15.5, 0.7), look_at=(0, 0, -0.05), lens=70)
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 15.5
cam.data.dof.aperture_fstop = 2.8

scene.frame_start, scene.frame_end = f0, f_rest
if a.get("still"):
    scene.frame_set(int(a["still"]))
    scene.render.filepath = os.path.join(out, f"still_{int(a['still']):04d}.png")
    bpy.ops.render.render(write_still=True)
else:
    if a.get("frames"):
        scene.frame_start, scene.frame_end = (int(x) for x in a["frames"].split("-"))
    bpy.ops.render.render(animation=True)
print("B1v2 done", f0, f_rest)
