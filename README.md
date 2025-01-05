# micro:bit blender remote thing?

![demo of microbit being wiggled around](assets/demo.gif)

2 files come with this:
 - `blender.py` intended to just be loaded up in blender
 - `blendernt.py` bug testing, not relying on any blender stuff

to install, you must:
 - compile this script from [makecode](http://makecode.microbit.com)... (1st is for serial, 2nd is for bluetooth)
 - ![serial blueprint code](assets/blueprint-serial.png)
 - ![bluetooth blueprint code](assets/blueprint-bluetooth.png)
 - install `pyserial` and make sure it's accessible by blender in `{PATH_TO_INSTALL}/Blender/{VERSION}/scripts/modules/serial/...`
 - open the scripting panel, and just paste the `blender.py` file into it, remember to change the `COM4` to whatever, like `/dev/ttyACM0` or whatnot
 - toggle the extension in the panel

now you can watch whatever object you have selected, wriggle around helplessly, the micro:bit does not have a great range of motion :P
