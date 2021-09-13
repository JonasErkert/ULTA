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

	collection_name: bpy.props.StringProperty(
		name="Collection Name",
		description="Collection of the new object",
		default="Extras"
	)

	@classmethod
	def poll(cls, context):
		return context.object.select_get() and context.object.type == 'MESH'

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		#self.join_multiuser()
		#self.quick_export_selected()
		self.create_bb_mesh()
		#self.activate_collection_of_selected_obj()
		return {'FINISHED'}

	def quick_export_selected(self):
		# Batch export to unreal from selected objects
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

			# Move to appropriate collection
			if current_collection[0].name != 'Mesh' or 'Rig' or 'Collision':
				if 'SM_' in obj.name:
					current_collection[0].objects.unlink(obj)
					mesh_collection.objects.link(obj)
				elif 'SK_' in obj.name:
					current_collection[0].objects.unlink(obj)
					rig_collection.objects.link(obj)
				elif 'UCX_' in obj.name:
					current_collection[0].objects.unlink(obj)
					collision_collection.objects.link(obj)
				else:
					# Default to mesh for now if object has no prefix
					current_collection[0].objects.unlink(obj)
					mesh_collection.objects.link(obj)

		try:
			bpy.ops.wm.send2ue()
		except AttributeError:
			print('Send2UE not installed!')

		# Move back to original collection
		for obj, coll_loc in obj_collection_dict.items():
			# print(obj.users_collection)
			obj.users_collection[0].objects.unlink(obj)
			coll_loc[0][0].objects.link(obj)

			if self.shift_origin:
				obj.location = coll_loc[1]

		bpy.context.view_layer.objects.active = active_obj

	def prefix_selected_objects(self):
		selected_objs = bpy.context.selected_objects
		static_mesh_prefix = 'SM_'
		skeletal_mesh_prefix = 'SK_'
		material_prefix = 'M_'

		# Rename meshes and armature
		for obj in selected_objs:
			obj_name = obj.name
			if obj.type == 'MESH' and static_mesh_prefix not in obj_name:
				obj.name = static_mesh_prefix + obj_name
			if obj.type == 'ARMATURE' and skeletal_mesh_prefix not in obj_name:
				obj.name = skeletal_mesh_prefix + obj.name

		# Rename materials
		for mat in bpy.data.materials:
			if material_prefix not in mat.name:
				mat.name = material_prefix + mat.name

	def mark_as_collision_primitives(self):
		collision_mesh_prefix = 'UCX_'
		# Check if already prefixed
		selected_objs = bpy.context.selected_objects
		for i, obj in enumerate(selected_objs):
			if collision_mesh_prefix not in obj.name:
				obj.name = collision_mesh_prefix + obj.name + '_0' + i

	def remove_substr_selected(self):
		for obj in bpy.context.selected_objects:
			name = obj.name
			obj.name = name.replace('_Blockout', '')

	def join_multiuser(self):
		# TODO: Poll if in object mode and if active object is selected when separate operator
		ctx = bpy.context
		selected_objs = bpy.context.selected_objects

		# Split into meshes and empty
		empty_obj = []
		for obj in selected_objs:
			if obj.type == 'EMPTY':
				empty_obj.append(obj)
				break

		selected_objs[:] = [only_meshes for only_meshes in selected_objs if not only_meshes.type == 'EMPTY']

		# Set active object, needed for joining later
		ctx.view_layer.objects.active = selected_objs[0]

		# Create collection
		coll_name = self.collection_name + 'Joined'
		coll_exists = False
		for coll in bpy.data.collections[self.collection_name].children.values():
			if coll_name in coll.name:
				coll_exists = True
				break

		new_collection = None
		if not coll_exists:
			new_collection = bpy.data.collections.new(coll_name)
			# Alternative: add to scene collection
			# ctx.scene.collection.children.link(new_collection)
			bpy.data.collections[self.collection_name].children.link(new_collection)
		else:
			new_collection = bpy.data.collections[coll_name]
		bpy.ops.object.select_all(action='DESELECT')

		# Duplicate meshes
		for obj in selected_objs:
			new_obj = obj.copy()
			new_obj.data = obj.data.copy()
			new_collection.objects.link(new_obj)
			ctx.view_layer.objects.active = new_obj
			new_obj.select_set(True)

			# Apply all modifiers
			for mod in [mods for mods in new_obj.modifiers]:
				bpy.ops.object.modifier_apply(modifier=mod.name)

		# Join objects
		bpy.ops.object.join()
		joined_obj = ctx.active_object
		joined_obj.name = self.collection_name + '_Joined'

		# Remove doubles
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.remove_doubles()
		bpy.ops.object.mode_set(mode='OBJECT')

		# Set origin to empty
		old_cursor_loc = ctx.scene.cursor.location
		ctx.scene.cursor.location = empty_obj[0].location
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
		ctx.scene.cursor.location = old_cursor_loc

	def create_bb_mesh(self):
		ctx = bpy.context
		selected_objs = ctx.selected_objects
		# Activate collection of selected object to add bb at correct place
		self.activate_collection_of_selected_obj()

		# Duplicate, then join meshes if there are multiple objects to get dimension of all objects
		# and keep the original pivot at the selected object
		bpy.ops.object.select_all(action='DESELECT')  # Deselect original object to avoid joining with new objects
		for obj in selected_objs:
			new_obj = obj.copy()
			new_obj.data = obj.data.copy()
			ctx.scene.collection.objects.link(new_obj)
			ctx.view_layer.objects.active = new_obj
			new_obj.select_set(True)
		bpy.ops.object.join()  # Throws warning if only 1 object is selected, ignore for now

		# Save object selected for  bounding box creation
		active_obj = ctx.active_object
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
		bpy.ops.mesh.primitive_cube_add()
		bound_box = ctx.active_object
		bound_box.name = 'UCX_' + selected_objs[0].name + '_01'

		# Set bb transform
		bound_box.dimensions = active_obj.dimensions
		bound_box.location = active_obj.location
		bound_box.rotation_euler = active_obj.rotation_euler

		# Set bb origin to selected mesh
		old_cursor_loc = Vector(ctx.scene.cursor.location)
		ctx.scene.cursor.location = selected_objs[0].location
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
		ctx.scene.cursor.location = old_cursor_loc

		# Delete duplicated object
		data_objs = bpy.data.objects
		data_objs.remove(data_objs[active_obj.name])

	# TODO: Check if working correctly
	def apply_modifiers_of_selected_objects(self):
		selected_objs = bpy.context.selected_objects

		for obj in selected_objs:
			if obj.type == 'MESH' or obj.type == 'CURVE':
				for mod in [mods for mods in obj.modifiers]:
					bpy.ops.object.modifier_apply(modifier=mod.name)

	# TODO: Check if working correctly
	def set_object_parent_collection_active(self, selected_obj):
		# This doesn't work, only gets correct key when creating new collection
		# collection = bpy.data.collections.new('My Collection')
		# bpy.context.scene.collection.children.link(collection)
		parent_collection = selected_obj.users_collection
		layer_collection = bpy.context.view_layer.layer_collection.children[parent_collection[0].name]
		bpy.context.view_layer.active_layer_collection = layer_collection

	def activate_collection_of_selected_obj(self):
		obj = bpy.context.object
		object_coll = obj.users_collection

		# Recursively transverse layer_collection for a particular name
		def recur_layer_collection(layer_coll, coll_name):
			found = None
			if layer_coll.name == coll_name:
				return layer_coll
			for layer in layer_coll.children:
				found = recur_layer_collection(layer, coll_name)
				if found:
					return found

		# Switching active Collection to active Object selected
		for coll in object_coll:
			layer_collection = bpy.context.view_layer.layer_collection
			layer_coll = recur_layer_collection(layer_collection, coll.name)
			bpy.context.view_layer.active_layer_collection = layer_coll


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
# Set origin to bottom of bounding box (+ set origin to middle of x and y of bounding box) bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
# Set origin to here (face, edge, vertex)
# Array modifier with randomization and "true" instancing, grid option, option to create one mesh or seperate object instances when applied

# Apply all modifiers
# Select parent collection of object