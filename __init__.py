bl_info = {
    "name": "Xoronaut",
    "author": "Joyce Jepleting",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "TOPBAR",
    "description": "Adds a custom menu item and properties panel to Blender",
    "category": "Object",
}
import csv
import bpy
import random
import math
import timeit
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector

xnt_name = 'Xoronaut'
numpts = 500
points_collection = None

# Define operator to select a CSV file
class SelectCSVFileOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "object.select_csv_file"
    bl_label = "Select CSV File"
    filename_ext = ".csv"

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Read the CSV file
        with open(self.filepath, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')

            # Get the first point for translation calculation
            first_point = None
            for row in csv_reader:
                first_point = Vector((float(row[0]), float(row[1]), float(row[2])))
                break

            # Reset the file reader
            file.seek(0)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Extract x, y, and z values
                x = float(row[0])
                y = float(row[1])
                z = float(row[2])

                # Apply translation to each point
                translation_vector = -1 * first_point
                translated_point = Vector((x, y, z)) + translation_vector

                # Create a new pyramid mesh in Blender
                bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, depth=1, location=translated_point)

        return {'FINISHED'}

# Add the file path property to the scene
bpy.types.Scene.filepath = StringProperty(name="CSV File Path", subtype='FILE_PATH')

# Define the panel for the file selection
class FileSelectionPanel(bpy.types.Panel):
    bl_label = "CSV File Selection"
    bl_idname = "OBJECT_PT_csv_file_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Display the file path text box and file picker
        layout.prop(scene, "filepath")
        layout.operator("object.select_csv_file")

# Register the operator and panel
classes = [SelectCSVFileOperator, FileSelectionPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    
class XoronautGeneratePointsOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_generate_points_operator"
    bl_label = "Generate Points"
    bl_description = "Generate n points in the start space"

    num_points: bpy.props.IntProperty(name="Number of Points", 
                                      default=numpts, 
                                      min=1, max=10000)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):   
        # Measure the time taken to generate points
        start_time = timeit.default_timer()
          
        radius = 100.0
        random.seed()
        wm = bpy.context.window_manager
        wm.progress_begin(0, self.num_points)
        
        points_collection = bpy.data.collections.new("Xoronaut_Points")
        bpy.context.scene.collection.children.link(points_collection)
        
        for _ in range(self.num_points):
            wm.progress_update(_)
            angle_rad = random.random() * 2 * math.pi
            radius_instance = math.sqrt(random.random()) * radius
            height = random.random() * 10.0
            x = radius_instance * math.cos(angle_rad)
            y = radius_instance * math.sin(angle_rad)
            z = height
            try:
                bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, depth=0.5)
                obj = bpy.context.active_object
                obj.location = (x, y, z)
                obj.data.use_fake_user = True
                obj.select_set(True)
                points_collection.objects.link(obj)
            except Exception as e:
                print("Overflow: {0} pts.".format(_))
                break

        wm.progress_end()
        
          # Calculate the time taken for point generation
        end_time = timeit.default_timer()
        execution_time = end_time - start_time

        self.report({'INFO'}, f"Generated {self.num_points} points in {execution_time:.5f} seconds.")
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

            self.report({'INFO'}, "Points cleared")
        else:
            self.report({'INFO'}, "No points found")
        points_collection = None
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

should_animate = False
fps = 30
animation_timer = None
def animate_points():
    global should_animate, fps

    if should_animate == False:
        return 5 / fps
    
    points_collection = bpy.data.collections.get("Xoronaut_Points")

    if not points_collection:
        return 5 / fps

    # animation code is in this for loop
    for obj in points_collection.objects:
        center_pt = obj.location
        hor_dist_to_center = \
                math.sqrt(center_pt.x ** 2 + center_pt.y ** 2)

        dz = 5 / hor_dist_to_center
        if hor_dist_to_center > 10:
            dz = 0

        radial_speed = -10 / hor_dist_to_center
        angular_speed = 10 / hor_dist_to_center
        angle_to_center = math.atan2(center_pt.y, center_pt.x)
        new_radius = hor_dist_to_center + radial_speed
        new_angle = angle_to_center + angular_speed
        new_x = new_radius * math.cos(new_angle)
        new_y = new_radius * math.sin(new_angle)
        dx = new_x - center_pt.x
        dy = new_y - center_pt.y
        obj.location.x += dx / fps
        obj.location.y += dy / fps
        obj.location.z += dz / fps

    return 1 / fps

class XoronautStartMotionOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_start_motion_operator"
    bl_label = "Start Motion"
    bl_description = "Start the points in motion using a velocity field equation"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        global animation_timer, should_animate
        if animation_timer is None:
            animation_timer = bpy.app.timers.register(animate_points)

        if should_animate == True:
            should_animate = False
            bl_label = "Start Motion"
            self.report({'INFO'}, "Motion stopped")
        else: # it's False, so
            should_animate = True
            bl_label = "Motion, Stop"
            self.report({'INFO'}, "Motion started")

        return {'FINISHED'}

class XoronautAnimateOperator(bpy.types.Operator):
    bl_idname = "object.xoronaut_animate_operator"
    bl_label = "Animate yo"
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
                    obj.keyframe_insert(data_path, frame=frame + frame_start)

        return {'FINISHED'}

class XoronautLoadPointsOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "object.xoronaut_load_points_operator"
    bl_label = "Load Points"
    bl_description = "Load points from a file"

    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        filepath = self.filepath

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
        #layout.operator("object.xoronaut_start_motion_operator")
        layout.operator("object.xoronaut_load_points_operator")

classes = (
    XoronautGeneratePointsOperator,
    XoronautClearPointsOperator,
    XoronautCountPointsOperator,
    XoronautStartMotionOperator,
    # XoronautAnimateOperator,
    XoronautLoadPointsOperator,
    XoronautPanel,
)

def draw_menu(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_xoronaut_menu", text=xnt_name)
class XoronautMenu(bpy.types.Menu):
    bl_label = "Xoronaut"
    bl_idname = "TOPBAR_MT_xoronaut_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.xoronaut_generate_points_operator")
        layout.operator("object.xoronaut_clear_points_operator")
        layout.operator("object.xoronaut_count_points_operator")
        layout.operator("object.xoronaut_start_motion_operator")
        # layout.operator("object.xoronaut_animate_operator")
        layout.operator("object.xoronaut_load_points_operator")

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
