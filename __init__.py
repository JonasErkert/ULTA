bl_info = {
    "name": "UlTA",
    "description": "Useful little tools for gamedev",
    "author": "Jonas Erkert",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Object",
}

import bpy

from . ulta_menus           import ULTA_MT_Pie_Menu
from . ulta_quick_export    import ULTA_QuickExport
from . ulta_join_multiuser  import ULTA_JoinMultiuser
from . ulta_create_bb       import ULTA_CreateBB
from . ulta_prefix_selected import ULTA_PrefixSelected
from . ulta_apply_modifiers import ULTA_ApplyModifiers

addon_keymaps = []

classes = (
    ULTA_QuickExport,
    ULTA_JoinMultiuser,
    ULTA_CreateBB,
    ULTA_PrefixSelected,
    ULTA_ApplyModifiers,
    ULTA_MT_Pie_Menu
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    # add keymap entry
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi_menu = km.keymap_items.new("wm.call_menu_pie", "COMMA", "PRESS", shift=True)
    kmi_menu.properties.name = ULTA_MT_Pie_Menu.bl_idname
    addon_keymaps.append((km, kmi_menu))


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
