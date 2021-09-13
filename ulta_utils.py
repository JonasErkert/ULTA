import bpy


def activate_collection_of_selected_obj():
    obj = bpy.context.object
    object_coll = obj.users_collection

    # recursively transverse layer_collection for a particular name
    def recur_layer_collection(layer_coll, coll_name):
        found = None
        if layer_coll.name == coll_name:
            return layer_coll
        for layer in layer_coll.children:
            found = recur_layer_collection(layer, coll_name)
            if found:
                return found

    # switching active Collection to active Object selected
    for coll in object_coll:
        layer_collection = bpy.context.view_layer.layer_collection
        layer_coll = recur_layer_collection(layer_collection, coll.name)
        bpy.context.view_layer.active_layer_collection = layer_coll

        # This doesn't work, only gets correct key when creating new collection
        # collection = bpy.data.collections.new('My Collection')
        # bpy.context.scene.collection.children.link(collection)
        # parent_collection = selected_obj.users_collection
        # layer_collection = bpy.context.view_layer.layer_collection.children[parent_collection[0].name]
        # bpy.context.view_layer.active_layer_collection = layer_collection
