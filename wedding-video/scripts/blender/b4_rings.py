"""B4 — ending insert: two wedding rings (one with a stone) are pulled together like magnets, pass
through each other and lock as linked rings, then turn slowly while a highlight runs across the gold.

Timing from insert start: approach 0 -> 4 beats (ease-in), link on beat 4, settle 4 -> 6, hold to 8.
blender -b -P scripts/blender/b4_rings.py -- --out renders/blender/b4/
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bpy  # noqa: E402
from common import (BEAT, args, area_light, camera, frame, key, reflection_cards, reset_scene,  # noqa: E402
                    set_easing, setup_render, srgb, world_studio)

a = args()
res = tuple(int(v) for v in a.get("res", "1920x1080").split("x"))
out = a.get("out", "renders/blender/b4/")
os.makedirs(out, exist_ok=True)

scene = reset_scene()
setup_render(scene, res=res, samples=int(a.get("samples", 32)), out=os.path.join(out, "f_"))
world_studio(scene, top="#FFF9F0", bottom="#CFC6B8", strength=0.35)
area_light("key", (-4, -5, 5), (50, 0, -35), (4, 3), 900, "#FFEBD2")
area_light("rim", (-3, 5, 3), (-60, 0, -150), (6, 0.8), 1600, "#FFE8D0")
reflection_cards(strength=4.0, color="#FFF6EA")
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -1.6))
bpy.context.active_object.is_shadow_catcher = True


def gold(name, hexcol):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(hexcol)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.13
    return m


def ring(name, mat, stone=False):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.14, major_segments=96, minor_segments=24)
    t = bpy.context.active_object
    t.name = name
    t.scale = (1, 1, 1.45)  # flatten the cross-section into a band
    bpy.ops.object.shade_smooth()
    t.data.materials.append(mat)
    root = bpy.data.objects.new(name + "_root", None)
    bpy.context.scene.collection.objects.link(root)
    t.parent = root
    if stone:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.22, location=(0, 1.3, 0))
        g = bpy.context.active_object
        g.scale = (1, 1.3, 1)
        gm = bpy.data.materials.new("stone")
        gm.use_nodes = True
        p = gm.node_tree.nodes["Principled BSDF"]
        p.inputs["Transmission Weight"].default_value = 1.0
        p.inputs["IOR"].default_value = 2.4
        p.inputs["Roughness"].default_value = 0.0
        g.data.materials.append(gm)
        g.parent = t
    return root


r = math.radians
# ring A stands in the XZ plane (faces camera), ring B in the YZ plane; offset by one radius they link
RA = ring("ringA", gold("goldA", "#E8C37A"), stone=True)
RB = ring("ringB", gold("goldB", "#F0D6A8"))
for o in RA.children:
    o.rotation_euler = (r(90), 0, 0)
for o in RB.children:
    o.rotation_euler = (r(90), 0, r(90))

lockA, lockB = (-0.5, 0, 0), (0.5, 0, 0)
f0, f_hit, f_settle, f_end = 1, frame(4 * BEAT), frame(6 * BEAT), frame(8 * BEAT)
key(RA, f0, location=(-6.0, 1.5, 1.2), rotation_euler=(r(40), r(-120), r(30)))
key(RB, f0, location=(6.0, 1.0, -1.0), rotation_euler=(r(-30), r(140), r(-20)))
key(RA, f_hit, location=lockA, rotation_euler=(r(4), r(-8), r(2)))
key(RB, f_hit, location=lockB, rotation_euler=(r(-3), r(9), r(-2)))
for o in (RA, RB):
    set_easing(o, f0, "EASE_IN", "QUAD")
key(RA, f_hit + 5, location=(-0.46, 0, 0.03), rotation_euler=(r(-2), r(3), 0))
key(RB, f_hit + 5, location=(0.46, 0, -0.03), rotation_euler=(r(2), r(-3), 0))
key(RA, f_settle, location=lockA, rotation_euler=(0, 0, 0))
key(RB, f_settle, location=lockB, rotation_euler=(0, 0, 0))

# the linked pair turns slowly together afterwards
pair = bpy.data.objects.new("pair", None)
bpy.context.scene.collection.objects.link(pair)
RA.parent = pair
RB.parent = pair
key(pair, 1, rotation_euler=(0, 0, r(-38)))
key(pair, f_settle, rotation_euler=(0, 0, r(-38)))
key(pair, f_end, rotation_euler=(0, 0, r(-14)), interpolation="LINEAR")

cam = camera(loc=(0, -9.4, 1.5), look_at=(0, 0, 0.3), lens=60)
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 9.5
cam.data.dof.aperture_fstop = 2.8
key(cam, f0, location=(0, -9.4, 1.5))
key(cam, f_end, location=(0, -8.8, 1.42), interpolation="LINEAR")

scene.frame_start, scene.frame_end = f0, f_end
if a.get("still"):
    scene.frame_set(int(a["still"]))
    scene.render.filepath = os.path.join(out, f"still_{int(a['still']):04d}.png")
    bpy.ops.render.render(write_still=True)
else:
    if a.get("frames"):
        scene.frame_start, scene.frame_end = (int(x) for x in a["frames"].split("-"))
    bpy.ops.render.render(animation=True)
print("B4 done", f_end)
