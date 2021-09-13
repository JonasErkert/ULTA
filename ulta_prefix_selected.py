import bpy
from bpy.types import Operator


class ULTA_PrefixSelected(Operator):
    bl_idname = "object.prefix_selected"
    bl_label = "Prefix Selected"
    bl_description = "Prefix selected objects with SM_, SK_ and materials with M_ or UCX"
    bl_options = {'REGISTER', 'UNDO'}

    is_collision_mesh: bpy.props.BoolProperty(
        name="Is Collision Mesh",
        description="Prefix with UCX_ and append _0x",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return context.object.select_get()

    def execute(self, context):
        selected_objs = bpy.context.selected_objects

        if not self.is_collision_mesh:
            static_mesh_prefix = 'SM_'
            skeletal_mesh_prefix = 'SK_'
            material_prefix = 'M_'

            # rename meshes and armature
            for obj in selected_objs:
                obj_name = obj.name
                if obj.type == 'MESH' and static_mesh_prefix not in obj_name:
                    obj.name = static_mesh_prefix + obj_name
                if obj.type == 'ARMATURE' and skeletal_mesh_prefix not in obj_name:
                    obj.name = skeletal_mesh_prefix + obj.name

            # rename materials
            for mat in bpy.data.materials:
                if material_prefix not in mat.name:
                    mat.name = material_prefix + mat.name
        else:
            collision_mesh_prefix = "UCX_"
            # check if already prefixed
            for i, obj in enumerate(selected_objs):
                if collision_mesh_prefix not in obj.name:
                    obj.name = collision_mesh_prefix + obj.name + "_0" + str(i+1)

        return {'FINISHED'}
