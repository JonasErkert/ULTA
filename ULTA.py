bl_info = {
    "name": "UlTA_Testing",
    "author": "Jonas Erkert",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "View3D > Object",
    "description": "Useful little tools for gamedev",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator


class OBJECT_OT_ulta(Operator):
    bl_label = "ULTA Testing"
    bl_idname = "object.ulta_testing"
    bl_description = "Useful little tools for gamedev"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        self.remove_substr_selected()
        return {'FINISHED'}

    def remove_substr_selected(self):
        for obj in bpy.context.selected_objects:
            name = obj.name
            obj.name = name.replace('_Blockout', '')


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_ulta.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_ulta)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_ulta)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
