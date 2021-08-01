bl_info = {
	"name": "UlTA",
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
from bpy.types import (
	AddonPreferences,
	Operator,
	Panel,
	PropertyGroup,
)
from mathutils import Vector


class OBJECT_OT_ulta(Operator):
	bl_label = "ULTA"
	bl_idname = "object.ulta"
	bl_description = "Useful little tools for gamedev"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_options = {'REGISTER', 'UNDO'}

	shift_origin: bpy.props.BoolProperty(
		name="Shift Origin",
		description="Move object to 0,0,0 before export",
		default=True
	)

	@classmethod
	def poll(cls, context):
		return context.object.select_get() and context.object.type == 'MESH'

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		# Batch export to unreal from selected objects
		objects = [object for object in bpy.context.selected_objects]
		active_obj = bpy.context.view_layer.objects.active
		obj_collection_dict = {}
		mesh_collection = bpy.data.collections['Mesh']

		for obj in objects:
			current_collection = obj.users_collection
			coll_loc_array = [current_collection, Vector(obj.location)]
			obj_collection_dict.update({obj: coll_loc_array})

			if self.shift_origin:
				obj.location = (0, 0, 0)

			# Don't move to mesh collection if it is already in there
			if current_collection[0].name != 'Mesh':
				current_collection[0].objects.unlink(obj)
				mesh_collection.objects.link(obj)

		try:
			bpy.ops.wm.send2ue()
		except AttributeError:
			print('Send2UE not installed!')

		for obj, coll_loc in obj_collection_dict.items():
			# print(obj.users_collection)
			obj.users_collection[0].objects.unlink(obj)
			coll_loc[0][0].objects.link(obj)

			if self.shift_origin:
				obj.location = coll_loc[1]

		bpy.context.view_layer.objects.active = active_obj

		return {'FINISHED'}

	# Prefix with SM_ and M_ and SK_
	def fix_naming(self):
		static_mesh_prefix = 'SM_'
		skeletal_mesh_prefix = 'SK_'
		material_prefix = 'M_'

		# Rename meshes and armature
		for obj in bpy.data.objects:
			obj_name = obj.name
			if obj.type == 'MESH' and static_mesh_prefix not in obj_name:
				obj.name = static_mesh_prefix + obj_name
			if obj.type == 'ARMATURE' and skeletal_mesh_prefix not in obj_name:
				obj.name = skeletal_mesh_prefix + obj.name

		# Rename materials
		for mat in bpy.data.materials:
			if material_prefix not in mat.name:
				mat.name = material_prefix + mat.name

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

# TODO
# Set origin to bottom of bounding box
# Set origin to here (face, edge, vertex)
