import bpy
from bpy.types import Operator
from mathutils import Vector


class ULTA_QuickExport(Operator):
    bl_idname = "object.quick_export"
    bl_label = "Quick Export"
    bl_description = "Quick export selected objects without moving them into the correct collection"
    bl_options = {'REGISTER', 'UNDO'}

    shift_origin: bpy.props.BoolProperty(
        name="Shift Origin",
        description="Move object to 0,0,0 before export",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH'

    def execute(self, context):
        objects = bpy.context.selected_objects
        active_obj = bpy.context.view_layer.objects.active
        obj_collection_dict = {}

        mesh_collection = bpy.data.collections['Mesh']
        rig_collection = bpy.data.collections['Rig']
        collision_collection = bpy.data.collections['Collision']

        for obj in objects:
            current_collection = obj.users_collection
            coll_loc_array = [current_collection, Vector(obj.location)]
            obj_collection_dict.update({obj: coll_loc_array})

            if self.shift_origin:
                obj.location = (0, 0, 0)

            # move to appropriate collection
            if current_collection[0].name != 'Mesh' or 'Rig' or 'Collision':
                if obj.name.startswith('SM_'):
                    current_collection[0].objects.unlink(obj)
                    mesh_collection.objects.link(obj)
                elif obj.name.startswith('SK_'):
                    current_collection[0].objects.unlink(obj)
                    rig_collection.objects.link(obj)
                elif obj.name.startswith('UCX_'):
                    current_collection[0].objects.unlink(obj)
                    collision_collection.objects.link(obj)
                else:
                    # Default to mesh for now if object has no prefix
                    current_collection[0].objects.unlink(obj)
                    mesh_collection.objects.link(obj)

        try:
            bpy.ops.wm.send2ue()
        except AttributeError:
            self.report({'WARNING'}, "Send2UE not installed!")

        # move back to original collection
        for obj, coll_loc in obj_collection_dict.items():
            obj.users_collection[0].objects.unlink(obj)
            coll_loc[0][0].objects.link(obj)

            if self.shift_origin:
                obj.location = coll_loc[1]

        bpy.context.view_layer.objects.active = active_obj
        return {'FINISHED'}
