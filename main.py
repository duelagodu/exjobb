from typing import Counter
import steppers
import time
import light
import casat_interface
import sensor
import json

evo = sensor.initEvo()
casat_interface.update_data()

last_item = casat_interface.get_item()
picked = casat_interface.is_picked()

debug = True

while(not steppers.arm):
    time.sleep(0.1)

while(True):

    # ---------------------------------------------------------------
    # Start of the main loop
    # ---------------------------------------------------------------

    # Go to 0, 0
    light.set_light(False)
    steppers.calibrate_X()
    steppers.calibrate_Y()
    time.sleep(0.2)

    # DEBUG
    if debug:
        print(casat_interface.get_item())
        print(casat_interface.get_mode())
        print(casat_interface.is_picked())
    

    # ---------------------------------------------------------------
    # Pick mode - Status: Finished
    # ---------------------------------------------------------------
    if casat_interface.get_mode() == 'Pick':

        # Move to curren position and turn on light
        steppers.move_to(casat_interface.get_x_axis(), casat_interface.get_y_axis(), steppers.stepper.SINGLE)

        # Measure the current height
        base_height = 0
        while True:
            for i in range(1000):
                sensor.get_evo_range(evo) # Flush out the first measurements
            base_height = sensor.get_evo_range(evo)
            if isinstance(base_height, int):
                break
        time.sleep(0.5)

        light.set_light(True)

        # DEBUG
        if debug:
            print('Base height: ' + str(base_height))

        # Look for variation bigger than the threshold
        height = sensor.get_evo_range(evo)
        threshold = 75 # mm
        trig_buffer = 50
        counter = 0
        while True:
            if base_height - height > threshold:
                if debug:
                    print(base_height - height)
                counter += 1
                time.sleep(0.01)
                if counter > trig_buffer:
                    picked = True
                    break
            if isinstance(height, int):
                height = sensor.get_evo_range(evo)
        
        # DEBUG
        if debug:
            print('Triggered height: ' + str(height))
        
        if picked:
            casat_interface.write_to_file('picked', 1)

        # Flash light to indicate that the item has been picked
        light.flash_light(True)
    # ---------------------------------------------------------------


    # ---------------------------------------------------------------
    # Place mode - Status: TODO
    # ---------------------------------------------------------------
    elif casat_interface.get_mode() == 'Place':
        print( 'Place mode not yet implemented' )
    # ---------------------------------------------------------------


    # ---------------------------------------------------------------
    # Setup mode - Status: Finished
    # ---------------------------------------------------------------
    elif casat_interface.get_mode() == 'Setup':
        light.set_light(True)
        while(casat_interface.is_picked() == False): # Exit setup mode by setting 'picked' to 1
            # Move to given position
            steppers.move_to(casat_interface.get_x_axis(), casat_interface.get_y_axis(), steppers.stepper.SINGLE)
            # Save current coordinates
            x = casat_interface.get_x_axis()
            y = casat_interface.get_y_axis()
            time.sleep(0.5)

            #DEBUG
            if debug:
                print('Current position: ' + str(x) + ', ' + str(y))

            # Wait for new coordinates
            while(x == casat_interface.get_x_axis() and y == casat_interface.get_y_axis()):
                try:
                    casat_interface.update_data()
                except ValueError:
                    print('Error loading file, trying again...')
                    time.sleep(0.5)
                    pass
        light.set_light(False)
    # ---------------------------------------------------------------


    # Wait and update for new item
    while(casat_interface.is_picked()):
        try:
            casat_interface.update_data()
            if debug:
                print(last_item)
                print(casat_interface.get_item())
                time.sleep(0.5)
        except ValueError:
            print('Error loading file, trying again...')
            time.sleep(0.5)
            pass
    
    # ---------------------------------------------------------------
    # End of the main loop
    # ---------------------------------------------------------------
