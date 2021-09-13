import bpy
from bpy.types import Operator


class ULTA_JoinMultiuser(Operator):
    bl_idname = "object.join_multiuser"
    bl_label = "Join Multiuser"
    bl_description = "Join multiuser objects to create a new mesh"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: bpy.props.StringProperty(
        name="Collection Name",
        description="Collection of the new object",
        default="Extras"
    )

    @classmethod
    def poll(cls, context):
        # TODO: poll if an active object is selected
        return context.object.select_get() and context.object.type == 'MESH'

    def execute(self, context):
        ctx = bpy.context
        selected_objs = bpy.context.selected_objects

        # split into meshes and empty
        # TODO: Handle no empty selected
        empty_obj = []
        for obj in selected_objs:
            if obj.type == 'EMPTY':
                empty_obj.append(obj)
                break

        selected_objs[:] = [only_meshes for only_meshes in selected_objs if not only_meshes.type == 'EMPTY']

        # set active object, needed for joining later
        ctx.view_layer.objects.active = selected_objs[0]

        # create collection
        coll_name = self.collection_name + 'Joined'
        coll_exists = False
        for coll in bpy.data.collections[self.collection_name].children.values():
            if coll_name in coll.name:
                coll_exists = True
                break

        new_collection = None
        if not coll_exists:
            new_collection = bpy.data.collections.new(coll_name)
            # alternative: add to scene collection
            # ctx.scene.collection.children.link(new_collection)
            bpy.data.collections[self.collection_name].children.link(new_collection)
        else:
            new_collection = bpy.data.collections[coll_name]
        bpy.ops.object.select_all(action='DESELECT')

        # duplicate meshes
        for obj in selected_objs:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_collection.objects.link(new_obj)
            ctx.view_layer.objects.active = new_obj
            new_obj.select_set(True)

            # apply all modifiers
            for mod in [mods for mods in new_obj.modifiers]:
                bpy.ops.object.modifier_apply(modifier=mod.name)

        # join objects
        bpy.ops.object.join()
        joined_obj = ctx.active_object
        joined_obj.name = self.collection_name + '_Joined'

        # remove doubles
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')

        # set origin to empty
        old_cursor_loc = ctx.scene.cursor.location
        ctx.scene.cursor.location = empty_obj[0].location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        ctx.scene.cursor.location = old_cursor_loc

        return {'FINISHED'}
