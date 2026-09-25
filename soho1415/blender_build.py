# -*- coding: utf-8 -*-
"""
GEOMETRY MASTER -> Blender シーン

    blender --background --python blender_build.py -- --save out/soho1415_master.blend

geometry_master.py と完全に同じ XY を使う。
「3D GEOMETRY APPROVED」後の室内パースは、新しいシーンを作らず
この .blend にカメラだけを追加して撮影する。

  CAMERA 1  バルコニー側 -> 入口方向
  CAMERA 2  入口側 -> バルコニー方向
  CAMERA 3  ミーティングテーブル付近 -> ワークスペース方向
  CAMERA 4  ワークスペース -> Living Dining 方向
  カメラ高 1500-1600 mm / フルサイズ換算 28-35 mm / 超広角禁止
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
import geometry_master as GM  # noqa: E402

S = 0.001  # mm -> m


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials):
        for d in list(c):
            c.remove(d)


def collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def add_box(b, name, coll):
    x0, x1, y0, y1, z0, z1 = b
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) * S, (y1 - y0) * S, (z1 - z0) * S)
    o.location = ((x0 + x1) / 2 * S, (y0 + y1) / 2 * S, (z0 + z1) / 2 * S)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)
    return o


def add_cyl(c, name, coll):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=c["r"] * S,
                                        depth=(c["z1"] - c["z0"]) * S)
    o = bpy.context.active_object
    o.name = name
    o.location = (c["cx"] * S, c["cy"] * S, (c["z0"] + c["z1"]) / 2 * S)
    for cc in list(o.users_collection):
        cc.objects.unlink(o)
    coll.objects.link(o)
    return o


def build():
    clear()
    made = 0
    for p in GM.parts():
        coll = collection(p["group"])
        objs = []
        for i, b in enumerate(p["boxes"]):
            objs.append(add_box(b, "%s_%02d" % (p["object"], i), coll))
        for i, c in enumerate(p["cylinders"]):
            objs.append(add_cyl(c, "%s_c%02d" % (p["object"], i), coll))
        if not objs:
            continue
        # 要求どおり 1 要素 = 1 オブジェクトに統合
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        if len(objs) > 1:
            bpy.ops.object.join()
        bpy.context.active_object.name = p["object"]
        made += 1
    print("built objects:", made)
    return made


if __name__ == "__main__":
    build()
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--save" in argv:
        path = argv[argv.index("--save") + 1]
        path = os.path.abspath(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("saved:", path)
