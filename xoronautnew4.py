bl_info = {
    "name": "Xoronaut",
    "author": "Joyce Jepleting",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "TOPBAR",
    "description": "Adds a custom menu item and properties panel to Blender",
    "category": "Object",
}

import bpy
import random


class XoronautGeneratePointsOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_generate_points_operator"
    bl_label = "Generate Points"
    bl_description = "Generate n points in the start space"

    num_points: bpy.props.IntProperty(name="Number of Points", default=5, min=1, max=100)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        # Generate n points in the start space
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()

        points_collection = bpy.data.collections.new("Xoronaut_Points")
        bpy.context.scene.collection.children.link(points_collection)

        for _ in range(self.num_points):
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.05, depth=0.1)
            obj = bpy.context.active_object
            obj.location = (
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0)
            )
            obj.data.use_fake_user = True
            obj.select_set(True)
            points_collection.objects.link(obj)

        return {'FINISHED'}


class XoronautClearPointsOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_clear_points_operator"
    bl_label = "Clear Points"
    bl_description = "Clear all the generated points"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        points_collection = bpy.data.collections.get("Xoronaut_Points")
        if points_collection:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in points_collection.objects:
                obj.select_set(True)
            bpy.ops.object.delete()

            bpy.data.collections.remove(points_collection)

            self.report({'INFO'}, "Points cleared")
        else:
            self.report({'INFO'}, "No points found")

        return {'FINISHED'}


class XoronautCountPointsOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_count_points_operator"
    bl_label = "Count Points"
    bl_description = "Count the number of generated points"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        points_collection = bpy.data.collections.get("Xoronaut_Points")
        if points_collection:
            count = len(points_collection.objects)
            self.report({'INFO'}, f"Number of Points: {count}")
        else:
            self.report({'INFO'}, "No points found")

        return {'FINISHED'}


class XoronautStartMotionOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_start_motion_operator"
    bl_label = "Start Motion"
    bl_description = "Start the points in motion using a velocity field equation"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        # Start the motion of the points using a velocity field equation
        # Add your custom motion logic here
        self.report({'INFO'}, "Motion started")
        return {'FINISHED'}


class XoronautAnimateOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_animate_operator"
    bl_label = "Animate"
    bl_description = "Animate the points over time"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        points_collection = bpy.data.collections.get("Xoronaut_Points")
        if points_collection:
            frame_start = 0
            frame_end = 100
            frame_count = frame_end - frame_start

            for obj in points_collection.objects:
                data_path = f"location"
                obj.animation_data_create()
                obj.animation_data.action = bpy.data.actions.new(name="Point Animation")
                fcurve = obj.animation_data.action.fcurves.new(data_path, index=0)
                keyframe_points = fcurve.keyframe_points

                for frame in range(frame_count):
                    z_value = obj.location[2]  # Z-axis value as the Y-axis value
                    keyframe_points.insert(frame + frame_start, z_value)

        return {'FINISHED'}


class XoronautPanel(bpy.types.Panel):
    bl_label = "Xoronaut Properties"
    bl_idname = "OBJECT_PT_xoronaut_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.xoronaut_generate_points_operator")
        layout.operator("object.xoronaut_clear_points_operator")
        layout.operator("object.xoronaut_count_points_operator")
        layout.operator("object.xoronaut_start_motion_operator")
        layout.operator("object.xoronaut_animate_operator")


classes = (
    XoronautGeneratePointsOperator,
    XoronautClearPointsOperator,
    XoronautCountPointsOperator,
    XoronautStartMotionOperator,
    XoronautAnimateOperator,
    XoronautPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def draw_menu(self, context):
    layout = self.layout
    layout.menu("TOPBAR_MT_xoronaut_menu", text="Xoronaut")


class XoronautMenu(bpy.types.Menu):
    bl_label = "Xoronaut"
    bl_idname = "TOPBAR_MT_xoronaut_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.xoronaut_generate_points_operator")
        layout.operator("object.xoronaut_clear_points_operator")
        layout.operator("object.xoronaut_count_points_operator")
        layout.operator("object.xoronaut_start_motion_operator")
        layout.operator("object.xoronaut_animate_operator")


def toggle_edit_mode():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')


def switch_to_edit_mode(func):
    def wrapper(*args, **kwargs):
        toggle_edit_mode()
        result = func(*args, **kwargs)
        toggle_edit_mode()
        return result

    return wrapper


@switch_to_edit_mode
def dummy_function():
    pass


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu)
    bpy.utils.register_class(XoronautMenu)


def unregister():
    bpy.utils.unregister_class(XoronautMenu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu)


if __name__ == "__main__":
    register()
