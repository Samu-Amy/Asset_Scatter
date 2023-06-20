import bpy
import os

bl_info = {
    "name": "Asset Scatter",
    "author": "Samuele Amisano",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N panel",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "COMMUNITY",
}

# -- TODO: la selezione di un oggetto o modificatore nella lista deve rendere attivo quell'oggetto o modificatore, se aggiungo uno scatter system con un oggetto selezionato non nella lista, deve selezionarne uno di default

# -- TODO: modifica il codice (sistema nomi e tutto) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# -- TODO: evita che vengano rimossi manualmente gli oggetti

# ------------------------------------------------------ FUNCTION ------------------------------------------------------

def get_prop_tab():
    for area in bpy.context.screen.areas:
        if area.type == 'PROPERTIES':
            return area.spaces[0].context
    
def set_prop_tab(data):
    for area in bpy.context.screen.areas:
        if area.type == 'PROPERTIES':
            area.spaces[0].context = data

#def updatePaintToggle(self, context):
#    
#    if bpy.context.mode == "PAINT_WEIGHT":
#        self.is_paint_mode = True
#    else:
#        self.is_paint_mode = False



# ------------------------------------------------------ PROPERTY ------------------------------------------------------

# Custom Properties
class AssetScatterProperties(bpy.types.PropertyGroup):
    
    old_prop_tab: bpy.props.StringProperty(
        name = "Old Prop Tab",
        description = "The Property tab opened before switch to weight paint via the add-on button"
    )
#    
#    is_paint_mode: bpy.props.BoolProperty(
#        name = "Paint Toggle",
#        description = "Switch Weight Paint mode",
#        default = False,
#        update = updatePaintToggle
#    )
    
#    scatter_groups = []



# --------------------------------------------------------- UI ---------------------------------------------------------

# Panel creation
class ASSETSCATTER_PT_main_panel(bpy.types.Panel):
    
    bl_label = "Asset Scatter"
    bl_idname = "ASSETSCATTER_PT_main_panel"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Asset Scatter'
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
#        asset_scatter_tool = scene.asset_scatter_tool
        
#        layout.operator("assetscatter.add_scatter_group", text="Scatter Group", icon="ADD")
        layout.operator("assetscatter.add_scatter_system", text="Scatter System", icon="ADD")
#        layout.operator("assetscatter.set_up")
#        layout.operator("assetscatter.paint_vertex_group")
#        layout.prop(AssetScatterProperties, "is_paint_mode", toggle=True, data=bpy.context.mode)
        
        if bpy.context.mode == "PAINT_WEIGHT":
            layout.operator("assetscatter.paint_vertex_group", text="Object Mode")
        else:
            layout.operator("assetscatter.paint_vertex_group", text="Paint Mode")
            
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("ASSETSCATTER_UL_scatter_groups", "", scn, "custom", scn, "custom_index", rows=rows)

        col = row.column(align=True)
        col.operator("assetscatter.add_scatter_group", text="", icon="ADD")
#        col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
        
        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.operator("custom.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM
        row = col.row(align=True)
        row = col.row(align=True)
        row.operator("custom.delete_object", icon="X") # NON ELIMINA GLI OGGETTI DAL FILE (solo dalla scen
        
        
        # Scatter Group List (lista di oggetti con geometry nodes)
        # Scatter System List (lista di modificatori legati allo Scatter Group)
        # -- TODO: nomina gli oggetti e i modificatori in base al numero di oggetti nella lista (e all'oggetto applicato)



# ------------------------------------------------------ OPERATOR ------------------------------------------------------

# Add a Scatter Group
class ASSETSCATTER_OT_add_scatter_group(bpy.types.Operator):
    
    bl_label = "Add Scatter Group"
    bl_idname = "assetscatter.add_scatter_group"
    
    
    def execute(self, context):
        
        # Check if the collection isn't created yet
        scatter_groups_collection_exist = False
        for col in bpy.data.collections:
            if col.name == "Asset Scatter - Scatter Groups": # -- TODO: usa variabile (se cambia il nome, cambia anche nella ricerca qua)
                scatter_groups_collection = col
                scatter_groups_collection_exist = True
                
        if not scatter_groups_collection_exist:
            scatter_groups_collection = bpy.data.collections.new("Asset Scatter - Scatter Groups")
            bpy.context.scene.collection.children.link(scatter_groups_collection)
            
        
        # Add Scatter Group Object
        bpy.ops.mesh.primitive_cube_add()
        scatter_group_object = bpy.context.active_object
        scatter_group_object.name = "Scatter Group" # -- TODO: rinomina in base al numero di oggetti già creati (se non richiede troppe risorse)
        
        # -- TODO: rendi invisibili gli Scatter Group Objects quando non hanno Scatter System (il cubo deve essere sempre nascosto)
        
        # Move Scatter Group Object into Scatter Groups Collection
        if scatter_groups_collection not in bpy.context.object.users_collection:
            scatter_groups_collection.objects.link(scatter_group_object)
            bpy.context.collection.objects.unlink(scatter_group_object)

        # Add List Object
        bpy.ops.custom.add_viewport_selection() # -- TODO: modifica operatore
        
        return {"FINISHED"}
    
    
# Add Scatter System
class ASSETSCATTER_OT_add_scatter_system(bpy.types.Operator):
    bl_label = "Add Scatter System"
    bl_idname = "assetscatter.add_scatter_system"
    
    def execute(self, context):
        file_path = "F:\Blender project\Gumroad-Blendermarket\Asset_Scatter.blend" # TODO: Da modificare per la release
        inner_path = "NodeTree"
        node_name = "Asset Scatter"

        
        # Check if the node group isn't imported yet
        if "Asset Scatter - Scatter Groups" not in bpy.data.node_groups:
            bpy.ops.wm.append(filepath=os.path.join(file_path, inner_path, node_name),directory=os.path.join(file_path, inner_path),filename=node_name)
        
        # Add Geometry Nodes modifier and select Asset Scatter node group
#        bpy.ops.object.modifier_add(type="NODES")
        mod = bpy.context.object.modifiers.new('as_geo_node','NODES')
        mod.node_group = bpy.data.node_groups["Asset Scatter"]
        return {"FINISHED"}

    
# Pain Vertex Group
class ASSETSCATTER_OT_paint_vertex_group(bpy.types.Operator):
    bl_label = "Paint"
    bl_idname = "assetscatter.paint_vertex_group"
    
    old_prop_context = ""
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None # -- TODO: controlla che l'oggetto abbia una modalità "weight paint"
    
    def execute(self, context):
        
        if bpy.context.mode != "PAINT_WEIGHT":
            old_prop_context = get_prop_tab()
        
        # Open Object Data Properties
        if context.mode != "PAINT_WEIGHT":
            set_prop_tab("DATA")
        elif self.old_prop_context != "":
            set_prop_tab(self.old_prop_context)
#        else:
#            set_prop_tab("RENDER")
            
        bpy.ops.paint.weight_paint_toggle()
        
        return {"FINISHED"}

    
    
#        return bpy.context.object.modifiers.new("GeometryNode", 'NODES')
#        return bpy.context.object.modifiers["GeometryNode"].node_group = bpy.data.node_groups['Asset Scatter']

# -- TODO: In questo caso crea il cubo e applica il primo modificatore, quindi si può attivare "isFirst", nel tasto per aggiungere altri non si attiva di default, anche se togliendo tutti i nodi e ne aggiunge altri il primo non avrebbe più "isFirst" (fare un controllo su
# quanti nodi "Asset Scatter" sono stati 

# -- TODO: dividi le parti in più file (UI, funzionamento, ecc) e togli il tasto setup, importa le cose in automatico quando si seleziona un oggetto (e metti una lista di oggetti selezionabili per poter gestire lo scatter su più oggetti)


# asset_scatter_object.modifiers_add(type='NODES')
# return asset_scatter_object.modifier_apply(modifier="Asset Scatter")


# ----------------------------------------------------------------------------------------------------------------------


import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class ASSETSCATTER_OT_actions(bpy.types.Operator):
    bl_idname = "assetscatter.list_action"
    bl_label = "Asset Scatter Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}
    
    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.scatter_group_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx+1].name
                scn.custom.move(idx, idx+1)
                scn.custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx-1].name
                scn.custom.move(idx, idx-1)
                scn.custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (scn.custom[idx].name)
                scn.custom_index -= 1
                scn.custom.remove(idx)
                self.report({'INFO'}, info)
                
#        if self.action == 'ADD':
#            if context.object:
#                item = scn.custom.add()
#                item.name = context.object.name
#                item.obj = context.object
#                scn.custom_index = len(scn.custom)-1
#                info = '"%s" added to list' % (item.name)
#                self.report({'INFO'}, info)
#            else:
#                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}
    

#class CUSTOM_OT_addViewportSelection(bpy.types.Operator):
#    """Add all items currently selected in the viewport"""
#    bl_idname = "custom.add_viewport_selection"
#    bl_label = "Add Viewport Selection to List"
#    bl_description = "Add all items currently selected in the viewport"
#    bl_options = {'REGISTER', 'UNDO'}
#    
#    def execute(self, context):
#        scn = context.scene
#        selected_objs = context.selected_objects
#        if selected_objs:
#            new_objs = []
#            for i in selected_objs:
#                item = scn.custom.add()
#                item.name = i.name
#                item.obj = i
#                new_objs.append(item.name)
#            info = ', '.join(map(str, new_objs))
#            self.report({'INFO'}, 'Added: "%s"' % (info))
#        else:
#            self.report({'INFO'}, "Nothing selected in the Viewport")
#        return{'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class ASSETSCATTER_UL_scatter_groups(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item.obj, "name", text="", emboss=False, translate=False, icon="MOD_PARTICLES")
            
    def invoke(self, context, event):
        pass   

#class CUSTOM_PT_objectList(bpy.types.Panel):
#    """Adds a custom panel to the TEXT_EDITOR"""
#    bl_idname = 'VIEW_PT_my_panel_demo'
#    bl_space_type = 'VIEW_3D'
#    bl_region_type = 'UI'
#    bl_category = "List"
#    bl_label = "Custom Object List demo"

#    def draw(self, context):
#        layout = self.layout
#        scn = bpy.context.scene

#        rows = 2
#        row = layout.row()
#        row.template_list("CUSTOM_UL_items", "", scn, "custom", scn, "custom_index", rows=rows)

#        col = row.column(align=True)
#        col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
#        col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
#        col.separator()
#        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
#        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
#        row = layout.row()
#        col = row.column(align=True)
#        row = col.row(align=True)
#        row.operator("custom.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM
#        row = col.row(align=True)
#        row.operator("custom.select_items", icon="VIEW3D", text="Select Item in 3D View")
#        row.operator("custom.select_items", icon="GROUP", text="Select All Items in 3D View").select_all = True
#        row = col.row(align=True)
#        row.operator("custom.delete_object", icon="X")


# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

class ASSETSCATTER_PG_scatterGroupsCollection(bpy.types.PropertyGroup):
    obj: PointerProperty(
        name="Object",
        type=bpy.types.Object)
    

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


# ---------------------------------------------------- REGISTRATION ----------------------------------------------------

_classes = [
    AssetScatterProperties,
    ASSETSCATTER_PT_main_panel,
    ASSETSCATTER_OT_add_scatter_group,
    ASSETSCATTER_OT_add_scatter_system,
    ASSETSCATTER_OT_paint_vertex_group,
    ASSETSCATTER_OT_actions,
#    CUSTOM_OT_addViewportSelection,
    ASSETSCATTER_UL_scatter_groups,
    ASSETSCATTER_PG_scatterGroupsCollection,]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.asset_scatter_pointer_properties = bpy.props.PointerProperty(type = AssetScatterProperties)
    bpy.types.Scene.asset_scatter_properties = CollectionProperty(type=ASSETSCATTER_PG_scatterGroupsCollection)
    bpy.types.Scene.scatter_group_index = IntProperty()


def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.asset_scatter_pointer_properties
    del bpy.types.Scene.asset_scatter_properties
    del bpy.types.Scene.scatter_group_index


# -- TODO: da togliere prima della release
if __name__ == "__main__":
    register()
