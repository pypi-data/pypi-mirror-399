# pybricks menu

Main menu for pybricks

Copyright (C) 2025 Joey Parrish

The pybricks firmware doesn't come with a menu or support for multiple programs
like the default Spike firmware.  This is a simple menu system and basic
startup checks to make it easier for kids to get started coding missions.

The startup checks ensure they don't start runs while plugged in, and show
battery status while charging.  If the battery level is too low on startup, a
warning animation will be shown.  Please charge to avoid inaccuracies caused by
low torque.

## Sample usage

```py
from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase

from pybricksmenu import main_menu, startup_checks


hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B, Direction.CLOCKWISE)
wheel_diameter = 175
wheel_separation = 200
drive = DriveBase(left_motor, right_motor, wheel_diameter, wheel_separation)
run = 1


def run1(drive: DriveBase) -> None:
    drive.straight(1000)


def run2(drive: DriveBase) -> None:
    drive.turn(720)


startup_checks(hub)

while True:
    run = main_menu(hub, num_items=9, item=run)
    if run == 1:
        run1(drive)
    elif run == 2:
        run2(drive)
```
