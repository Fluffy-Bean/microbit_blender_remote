from kaspersmicrobit import KaspersMicrobit
from kaspersmicrobit.errors import KaspersMicrobitNotFound
import time


ROTATION_PITCH  = "rp"
ROTATION_ROLL   = "rr"
COMPASS_HEADING = "ch"
ACCELERATION_X  = "ax"
ACCELERATION_Y  = "ay"
ACCELERATION_Z  = "az"
RESET_POSITION  = "r"


class Microbit:
    def __init__(self):
        self.rotation_pitch = 0
        self.rotation_roll  = 0

        self.compass_heading = 0

        self.acceleration_x = 0
        self.acceleration_y = 0
        self.acceleration_z = 0

        self.bluethooth_connection = KaspersMicrobit.find_one_microbit()

        self.service_running = False

    def start(self):
        try:
            self.bluethooth_connection.connect()
            # Only run the thread if the bluetooth connection successful AND has the uart service
            self.service_running = self.bluethooth_connection.uart.is_available()
            self.bluethooth_connection.uart.receive_string(self.update)
        except KaspersMicrobitNotFound:
            self.service_running = False

    def stop(self):
        self.bluethooth_connection.disconnect()

    def update(self, line):
        if self.service_running:
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


microbit = Microbit()
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
