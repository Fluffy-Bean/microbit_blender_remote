import bpy
import serial
import threading
import time
import math


ROTATION_PITCH  = "rp"
ROTATION_ROLL   = "rr"
COMPASS_HEADING = "ch"
ACCELERATION_X  = "ax"
ACCELERATION_Y  = "ay"
ACCELERATION_Z  = "az"
RESET_POSITION  = "r"


class Microbit:
    def __init__(self, port, baudrate=115200):
        self.rotation_pitch = 0
        self.rotation_roll  = 0

        self.compass_heading = 0

        self.acceleration_x = 0
        self.acceleration_y = 0
        self.acceleration_z = 0

        self.serial_connection          = serial.Serial()
        self.serial_connection.baudrate = baudrate
        self.serial_connection.port     = port

        self.thread_running = False
        self.thread         = None
        self.thread_lock    = threading.Lock()

    def start(self):
        self.serial_connection.open()

        # Only run the thread of the serial connection successful
        self.thread_running = self.serial_connection.is_open
        self.thread         = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def stop(self):
        with self.thread_lock:
            if self.thread:
                self.thread_running = False
                self.thread.join()

            self.serial_connection.close()

    def update(self):
        while self.thread_running:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode("utf-8").strip()

                with self.thread_lock:
                    if line.startswith(ROTATION_PITCH):
                        self.rotation_pitch = int(line[3:])
                    elif line.startswith(ROTATION_ROLL):
                        self.rotation_roll = int(line[3:])
                    elif line.startswith(COMPASS_HEADING):
                        self.compass_heading = int(line[3:])
                    elif line.startswith(ACCELERATION_X):
                        self.acceleration_x = int(line[3:])
                    elif line.startswith(ACCELERATION_Y):
                        self.acceleration_y = int(line[3:])
                    elif line.startswith(ACCELERATION_Z):
                        self.acceleration_z = int(line[3:])
                    else:
                        print("Error reading serial:", line)
            else:
                time.sleep(0.1)


microbit     = Microbit("COM4")
loop_enabled = False


def update_microbit_data():
    global microbit

    with microbit.thread_lock:
        obj = bpy.context.active_object
        if obj:
            obj.rotation_euler[0] = microbit.rotation_roll * -0.01
            obj.rotation_euler[1] = microbit.rotation_pitch * 0.01

            # obj.rotation_euler[2] = math.radians(microbit.compass_heading)

            # obj.location.x = microbit.acceleration_x * 0.01
            # obj.location.y = microbit.acceleration_y * 0.01
            # obj.location.z = microbit.acceleration_z * 0.01

            print("  Rotation Pitch :: " + str(microbit.rotation_pitch))
            print("   Rotation Roll :: " + str(microbit.rotation_roll))
            print(" Compass Heading :: " + str(microbit.compass_heading))
            print("  Acceleration X :: " + str(microbit.acceleration_x))
            print("  Acceleration Y :: " + str(microbit.acceleration_y))
            print("  Acceleration Z :: " + str(microbit.acceleration_z))
            print("=================::=================")

    return 0.05


def toggle_loop():
    global loop_enabled, microbit

    if loop_enabled:
        microbit.stop()
        microbit     = None
        loop_enabled = False

        print("Background loop stopped.")
    else:
        loop_enabled = True
        microbit     = Microbit("COM4")
        microbit.start()

        bpy.app.timers.register(update_microbit_data, first_interval=0.1)

        print("Background loop started.")


class MicrobitOperator(bpy.types.Operator):
    bl_idname = "object.toggle_background_loop"
    bl_label  = "Toggle Background Loop"

    def execute(self, context):
        toggle_loop()
        return {"FINISHED"}


class MicrobitPanel(bpy.types.Panel):
    bl_label       = "Microbit Control"
    bl_idname      = "OBJECT_PT_microbit_control"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Tool"

    def draw(self, context):
        global loop_enabled

        layout = self.layout
        layout.operator("object.toggle_background_loop", text=f"Toggle Loop {'[ON]' if loop_enabled else '[OFF]'}")


def register():
    bpy.utils.register_class(MicrobitOperator)
    bpy.utils.register_class(MicrobitPanel)


def unregister():
    global loop_enabled

    if loop_enabled:
        # Yeet serial connection + thread
        toggle_loop()

    bpy.utils.unregister_class(MicrobitOperator)
    bpy.utils.unregister_class(MicrobitPanel)


if __name__ == "__main__":
    register()
