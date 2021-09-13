import bpy
from bpy.types import Operator
from mathutils import Vector
from . ulta_utils import activate_collection_of_selected_obj


class ULTA_CreateBB(Operator):
    bl_idname = "object.create_bb"
    bl_label = "Create BB"
    bl_description = "Create a bounding box for the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH'

    def execute(self, context):
        ctx = bpy.context
        selected_objs = ctx.selected_objects
        # activate collection of selected object to add bb at correct place
        activate_collection_of_selected_obj()

        # duplicate, then join meshes if there are multiple objects to get dimension of all objects
        # and keep the original pivot at the selected object
        bpy.ops.object.select_all(action='DESELECT')  # Deselect original object to avoid joining with new objects
        for obj in selected_objs:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            ctx.scene.collection.objects.link(new_obj)
            ctx.view_layer.objects.active = new_obj
            new_obj.select_set(True)
        bpy.ops.object.join()  # throws warning if only 1 object is selected, ignore for now

        # save object selected for  bounding box creation
        active_obj = ctx.active_object
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.mesh.primitive_cube_add()
        bound_box = ctx.active_object
        bound_box.name = 'UCX_' + selected_objs[0].name + '_01'

        # set bb transform
        bound_box.dimensions = active_obj.dimensions
        bound_box.location = active_obj.location
        bound_box.rotation_euler = active_obj.rotation_euler

        # display as wire checkbox
        bound_box.display_type = 'WIRE'

        # Set bb origin to selected mesh
        old_cursor_loc = Vector(ctx.scene.cursor.location)
        ctx.scene.cursor.location = selected_objs[0].location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        ctx.scene.cursor.location = old_cursor_loc

        # delete duplicated object
        data_objs = bpy.data.objects
        data_objs.remove(data_objs[active_obj.name])
        return {'FINISHED'}
