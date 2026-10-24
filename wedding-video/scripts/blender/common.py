"""Shared helpers for the wedding-video Blender inserts (run inside `blender -b -P`).

Conventions
- 30 fps, frame 1 = insert time 0. Timing helpers take seconds or beats (104 BPM).
- Transparent film; renders PNG RGBA sequences that ffmpeg turns into VP9-alpha WebM.
- Colours are the film's tokens (sRGB hex -> linear for Blender).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONTS = os.path.join(ROOT, "assets", "fonts")
FPS = 30
BPM = 104.0
BEAT = 60.0 / BPM

COLORS = {
    "cobalt": "#2F3BFF",
    "pink": "#FF5C8A",
    "lilac": "#C9B6FF",
    "violet": "#6A2BD9",
    "cream": "#F3EEE3",
    "ink": "#111111",
    "red": "#FF2D55",
    "gold": "#E8C37A",
    "mint": "#9FF0D2",
}


def args():
    """Arguments after `--` on the blender command line, as a dict of --key value."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    for i, a in enumerate(argv):
        if a.startswith("--"):
            nxt = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else "1"
            out[a[2:]] = nxt
    return out


def frame(seconds):
    return 1 + round(seconds * FPS)


def beats(n):
    return n * BEAT


def srgb(hexstr, alpha=1.0):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, alpha)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 1
    return scene


def setup_render(scene, res=(1920, 1080), samples=48, engine="CYCLES", out=None):
    engine = os.environ.get("FORCE_ENGINE", engine)
    scene.render.engine = engine
    if engine.startswith("BLENDER_EEVEE"):
        e = scene.eevee
        e.taa_render_samples = max(16, samples)
        if hasattr(e, "use_raytracing"):
            e.use_raytracing = True
        if hasattr(e, "use_shadows"):
            e.use_shadows = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 15
    # Standard keeps the film's brand colours (#2F3BFF, #FF5C8A) exact instead of AgX's desaturation
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if engine == "CYCLES":
        c = scene.cycles
        c.device = "CPU"
        c.samples = samples
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.03
        c.use_denoising = True
        c.denoiser = "OPENIMAGEDENOISE"
        c.max_bounces = 4
        c.diffuse_bounces = 1
        c.glossy_bounces = 2
        c.transmission_bounces = 3
        c.adaptive_min_samples = 4
        c.caustics_reflective = False
        c.caustics_refractive = False
        scene.render.use_persistent_data = True
    if out:
        scene.render.filepath = out


def world_studio(scene, top="#F3EEE3", bottom="#C9B6FF", strength=1.0):
    """Soft gradient world: reads as a studio cyclorama in reflections, invisible with film_transparent."""
    world = bpy.data.worlds.new("studio")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    grad_coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = srgb(bottom)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = srgb(top)
    maprange = nt.nodes.new("ShaderNodeMapRange")
    maprange.inputs["From Min"].default_value = -1
    maprange.inputs["From Max"].default_value = 1
    nt.links.new(grad_coord.outputs["Generated"], sep.inputs[0])
    # use the view-space Z of the generated direction for a vertical gradient
    nt.links.new(sep.outputs["Z"], maprange.inputs["Value"])
    nt.links.new(maprange.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return world


def area_light(name, loc, rot, size, energy, color="#FFFFFF"):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE"
    data.size, data.size_y = size if isinstance(size, tuple) else (size, size)
    data.energy = energy
    data.color = srgb(color)[:3]
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    obj.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.scene.collection.objects.link(obj)
    return obj


def reflection_cards(strength=6.0, color="#FFFFFF"):
    """Emissive softbox planes seen only in reflections: they give chrome and gloss crisp highlights."""
    cards = []
    for name, loc, rot, size in (
        ("card_top", (0, -2, 7), (0, 0, 0), (14, 4)),
        ("card_left", (-8, -3, 1), (90, 0, -70), (3, 8)),
        ("card_right", (8, -3, 1), (90, 0, 70), (3, 8)),
        ("card_back", (0, 9, 2), (90, 0, 0), (16, 3)),
    ):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=[math.radians(a) for a in rot])
        p = bpy.context.active_object
        p.name = name
        p.scale = (size[0], size[1], 1)
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = strength
        em.inputs["Color"].default_value = srgb(color)
        o = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], o.inputs[0])
        p.data.materials.append(m)
        p.visible_camera = False
        p.visible_shadow = False
        cards.append(p)
    return cards


def three_point(key=900, fill=250, rim=1200):
    area_light("key", (4, -5, 6), (50, 0, 35), (5, 3), key)
    area_light("fill", (-6, -3, 2), (75, 0, -60), (6, 4), fill, "#E8E4FF")
    area_light("rim", (0, 6, 5), (-55, 0, 180), (8, 1.2), rim, "#FFE9F1")


def camera(loc=(0, -12, 0), look_at=(0, 0, 0), lens=50, dof_target=None, fstop=2.8):
    data = bpy.data.cameras.new("cam")
    data.lens = lens
    cam = bpy.data.objects.new("cam", data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    point_at(cam, look_at)
    bpy.context.scene.camera = cam
    if dof_target is not None:
        data.dof.use_dof = True
        data.dof.focus_object = dof_target
        data.dof.aperture_fstop = fstop
    return cam


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def font(name):
    path = os.path.join(FONTS, name)
    for f in bpy.data.fonts:
        if f.filepath == path:
            return f
    return bpy.data.fonts.load(path)


def text_mesh(body, font_file, size=1.0, extrude=0.12, bevel=0.03, bevel_res=4, name=None,
              align="CENTER", to_mesh=True):
    """Hangul-safe 3D text. Returns the object (converted to mesh when to_mesh)."""
    curve = bpy.data.curves.new(name or f"txt_{body}", "FONT")
    curve.body = body
    curve.font = font(font_file)
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = bevel
    curve.bevel_resolution = bevel_res
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.resolution_u = 6
    obj = bpy.data.objects.new(name or f"txt_{body}", curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.rotation_euler = (math.radians(90), 0, 0)  # stand upright facing -Y (the camera)
    if to_mesh:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.convert(target="MESH")
        obj.select_set(False)
    return obj


def inflate(obj, voxel=0.018, smooth_iters=12, smooth_factor=0.9, displace=0.0):
    """Balloon look: voxel remesh closes the letter into one volume, then corrective smoothing rounds it."""
    rem = obj.modifiers.new("remesh", "REMESH")
    rem.mode = "VOXEL"
    rem.voxel_size = voxel
    rem.adaptivity = 0
    sm = obj.modifiers.new("smooth", "SMOOTH")
    sm.iterations = smooth_iters
    sm.factor = smooth_factor
    if displace:
        disp = obj.modifiers.new("puff", "DISPLACE")
        disp.strength = displace
        disp.direction = "NORMAL"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    return obj


def mat_glossy(name, hexcolor, roughness=0.18, sss=0.15, coat=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(hexcolor)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = (0.4, 0.2, 0.2)
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.06
    return m


def mat_chrome(name, tint="#2F3BFF", roughness=0.08, metallic=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(tint)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Coat Weight"].default_value = 0.3
    return m


def mat_plastic(name, hexcolor, roughness=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = srgb(hexcolor)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Specular IOR Level"].default_value = 0.5
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def key(obj, frame_no, interpolation="BEZIER", **props):
    """Insert keys: key(obj, 10, location=(0,0,0), rotation_euler=(...), scale=(...))."""
    for prop, value in props.items():
        setattr(obj, prop, value)
        obj.keyframe_insert(data_path=prop, frame=frame_no)
    if obj.animation_data and obj.animation_data.action:
        for fc in _fcurves(obj.animation_data.action):
            for kp in fc.keyframe_points:
                if int(kp.co[0]) == frame_no:
                    kp.interpolation = interpolation


def _fcurves(action):
    if hasattr(action, "fcurves") and action.fcurves:
        return action.fcurves
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def set_easing(obj, frame_no, easing="EASE_OUT", interpolation="EXPO"):
    for fc in _fcurves(obj.animation_data.action):
        for kp in fc.keyframe_points:
            if int(kp.co[0]) == frame_no:
                kp.interpolation = interpolation
                kp.easing = easing


def render_animation(scene, start, end):
    scene.frame_start, scene.frame_end = start, end
    bpy.ops.render.render(animation=True)
