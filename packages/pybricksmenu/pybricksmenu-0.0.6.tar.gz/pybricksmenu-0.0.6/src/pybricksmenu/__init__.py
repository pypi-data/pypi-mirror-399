# Main menu for pybricks
#
# Copyright (C) 2025 Joey Parrish
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Main menu for pybricks

The pybricks firmware doesn't come with a menu or support for multiple programs
like the default Spike firmware.  This is a simple menu system and basic
startup checks to make it easier for kids to get started coding missions.

The startup checks ensure they don't start runs while plugged in, and show
battery status while charging.  If the battery level is too low on startup, a
warning animation will be shown.  Please charge to avoid inaccuracies caused by
low torque.

Sample usage:


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
"""

from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Color, Icon, Side
from pybricks.tools import wait


# These are both in mV (millivolts).
# 8.3V is fully charged, even if the charger would continue topping up.
FULL_VOLTAGE_THRESHOLD = 8300

# Below this voltage, we do not get consistent results.
# Reddit recommends 8.0V, but this is what we chose.
# Source: https://www.reddit.com/r/FLL/comments/1h7du3f/comment/mdbmhsf/
LOW_VOLTAGE_THRESHOLD = 7900

# After this much idle time in the menu, shut down.
MENU_TIMEOUT_SECONDS = 120.0


def wait_for_button(hub: PrimeHub, timeout_seconds: float) -> set[Button]:
    """Wait for a button to be pressed, then return the pressed buttons.

    Returns a `Set` of `Button` values when the buttons are released.

    Whichever buttons are released last are the ones returned.

    To see if a particular button was pressed, use something like:

    ```py
        from pybricks.parameters import Button
        from menu import wait_for_button

        pressed = wait_for_button(hub, timeout_seconds=10.0)
        if Button.LEFT in pressed:
            print('Left button pressed!')
    ```
    """

    # Keep track of the time.
    seconds_remaining = timeout_seconds

    # Wait for any buttons to be pressed, and record them.
    pressed = []
    while not any(pressed) and seconds_remaining > 0.0:
        pressed = hub.buttons.pressed()
        wait(10)
        seconds_remaining -= 10 / 1000

    # Wait for all buttons to be released.
    while any(hub.buttons.pressed()) and seconds_remaining > 0.0:
        wait(10)
        seconds_remaining -= 10 / 1000

    if seconds_remaining < 0.0:
      raise TimeoutError(
          f'Timeout waiting for menu selection after {timeout_seconds}')

    # Return the set of pressed buttons.
    return pressed


def main_menu(hub: PrimeHub, num_items: int, item: int = 1) -> int:
    """Display a numerical menu.

    Press left to go down, right to go up, and the center button to choose an
    item.  Returns the number (from 1 to `num_items`) of the chosen item.

    To quit to the bootloader, press the bluetooth button.

    Sample usage:

    ```py
        # The default run to show in the menu.
        run = 1

        while True:
            # Show the menu and wait for a choice.
            run = main_menu(hub, num_items = 9, item = run)

            # Run the chosen run and the loop back to the menu.
            if run == 1:
                run1(drive)
            elif run == 2:
                run2(drive)
    ```
    """

    # The user can always hold the center button to shut down.  While in the
    # menu, the user can also press bluetooth together to quit.
    hub.system.set_stop_button(Button.BLUETOOTH)

    # Use this to indicate that we're waiting for input.
    hub.light.on(Color.GREEN)

    # Set the speaker volume to 50% so our feedback beeps aren't too loud.
    hub.speaker.volume(50)

    while True:
        # Show the number of the selected item.
        if item < 10:
            hub.display.char(str(item))
        else:
            hub.display.number(item)

        # Wait for buttons to be pressed.
        try:
            pressed = wait_for_button(hub, timeout_seconds=MENU_TIMEOUT_SECONDS)
        except TimeoutError as e:
            print(e)
            hub.system.shutdown()
            sys.exit(0)

        if Button.LEFT in pressed:
            # Go down, and wrap around if needed.
            item -= 1
            if item < 1:
                item = num_items
        elif Button.RIGHT in pressed:
            # Go up, and wrap around if needed.
            item += 1
            if item > num_items:
                item = 1
        elif Button.CENTER in pressed:
            # The user picked something.
            break

        # Beep in confirmation of the button press.
        hub.speaker.beep(frequency=300, duration=100)

    # Beep in confirmation of the choice.
    hub.speaker.beep(frequency=500, duration=100)

    # Use this to indicate that we're running.
    hub.light.on(Color.MAGENTA)

    # Return the item the user picked.
    return item


def _charger_status_name(status: int) -> str:
    if status == 0:
        return 'unplugged'
    elif status == 1:
        return 'charging'
    elif status == 2:
        return 'charged'
    elif status == 3:
        return 'error'
    else:
        return 'unknown ({})'.format(status)


def startup_checks(hub):
    """Run startup checks to make sure it's safe to run.

    Checks charger status and waits until the robot is unplugged.

    Before returning, it checks the robot's battery level.  If it's too low for
    accuracy (too low for consistent torque), it shows a warning animation
    (spinning sad face) on the display for 3 seconds.

    Call this before your menu loop.  (`while True: main_menu(...)`)
    """

    # Check charging status.  We don't want to show the menu and allow programs
    # to run while plugged in.
    status = hub.charger.status()
    voltage = hub.battery.voltage()
    print('Battery status', _charger_status_name(status),
          'voltage', voltage, 'mV')

    while status != 0:  # Not unplugged
        if status == 1:  # Charging
            if voltage < FULL_VOLTAGE_THRESHOLD:
                icon = Icon.PAUSE
            else:
                icon = Icon.TRUE
        elif status == 2:  # Charged
            icon = Icon.TRUE
        elif status == 3:  # Error
            icon = Icon.SAD
        else:
            icon = Icon.FALSE

        # So long as we're plugged in, keep showing the icon.
        hub.display.icon(icon)
        wait(1000)
        status = hub.charger.status()
        voltage = hub.battery.voltage()
        print('Battery status', _charger_status_name(status),
              'voltage', voltage, 'mV')

    # If the voltage is low, show a warning animation, but return and let the
    # user decide if they want to use it.
    if hub.battery.voltage() < LOW_VOLTAGE_THRESHOLD:
        print('Low voltage!  Please charge me!')
        for side in [Side.TOP, Side.RIGHT, Side.BOTTOM, Side.LEFT, Side.TOP]:
            hub.display.orientation(side)
            hub.display.icon(Icon.SAD)
            wait(500)
        wait(500)


if __name__ == '__main__':
    # A simple test program for the menu.
    hub = PrimeHub()

    print('Running menu demo...')
    hub.display.icon(Icon.CIRCLE)
    wait(3000)

    startup_checks(hub)

    chosen = 1
    while True:
        chosen = main_menu(hub, 12, chosen)
        hub.display.icon(Icon.HEART)
        wait(3000)
