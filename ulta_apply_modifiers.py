import bpy
from bpy.types import Operator


class ULTA_ApplyModifiers(Operator):
    bl_idname = "object.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Apply all modifiers of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object.select_get()

    def execute(self, context):
        selected_objs = bpy.context.selected_objects

        for obj in selected_objs:
            if obj.type == 'MESH' or obj.type == 'CURVE':
                for mod in [mods for mods in obj.modifiers]:
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        return {'FINISHED'}
