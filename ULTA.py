import bpy
from mathutils import *


# Batch export to unreal from selected objects
def batch_export_selected():
	objects = [object for object in bpy.context.selected_objects]
	active_obj = bpy.context.view_layer.objects.active
	obj_collection_dict = {}
	mesh_collection = bpy.data.collections['Mesh']

	for obj in objects:
		current_collection = obj.users_collection
		coll_loc_array = [current_collection, Vector(obj.location)]
		obj_collection_dict.update({obj: coll_loc_array})
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
		obj.location = coll_loc[1]

	bpy.context.view_layer.objects.active = active_obj


# Prefix with SM_ and M_ and SK_
def fix_naming():
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


def remove_substr_selected():
	for obj in bpy.context.selected_objects:
		name = obj.name
		obj.name = name.replace('_Blockout', '')


# TODO
# Set origin to bottom of bounding box
# Set origin to here (face, edge, vertex)
