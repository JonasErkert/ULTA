import bpy
from bpy.types import Menu


class ULTA_MT_Pie_Menu(Menu):
    bl_idname = "ULTA_MT_Pie_Menu"
    bl_label = "ULTA Operations"

    def draw(self, context):
        active_obj = bpy.context.view_layer.objects.active
        layout = self.layout
        pie = layout.menu_pie()

        if active_obj:
            mode = active_obj.mode
            if mode == 'OBJECT':
                pie.operator('object.quick_export',     icon='EXPORT')
                pie.operator('object.join_multiuser',   icon='MOD_BUILD')
                pie.operator('object.create_bb',        icon='CUBE')
                pie.operator('object.prefix_selected',  icon='SYNTAX_OFF')
                pie.operator('object.apply_modifiers',  icon='MODIFIER')
