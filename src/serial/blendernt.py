import serial
import threading
import time


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

        # Only run the thread if the serial connection successful
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


microbit = Microbit("COM4")
loop_enabled = False


def toggle_loop():
    global loop_enabled

    if loop_enabled:
        loop_enabled = False
        microbit.stop()
        print("Background loop stopped.")
    else:
        loop_enabled = True
        microbit.start()
        print("Background loop started.")


if __name__ == "__main__":
    toggle_loop()

    while True:
        try:
            with microbit.thread_lock:
                print("  Rotation Pitch :: " + str(microbit.rotation_pitch))
                print("   Rotation Roll :: " + str(microbit.rotation_roll))
                print(" Compass Heading :: " + str(microbit.compass_heading))
                print("  Acceleration X :: " + str(microbit.acceleration_x))
                print("  Acceleration Y :: " + str(microbit.acceleration_y))
                print("  Acceleration Z :: " + str(microbit.acceleration_z))
                print("=================::=================")
            time.sleep(0.05)
        except KeyboardInterrupt:
            break

    if loop_enabled:
        toggle_loop()
