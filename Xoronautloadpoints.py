import csv
import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector

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
