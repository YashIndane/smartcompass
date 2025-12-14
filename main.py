#!/usr/bin/python3

# Main Smart Compass code

# Usage -
   
#   Pulling the container -
#   $ sudo docker pull --platform linux/arm64/v8 docker.io/yashindane/smartcompass:latest

#   Running the container -
#   $ sudo docker run -it --platform linux/arm64/v8 --name smartcompass-con.$(date "+%Y.%m.%d-%H.%M.%S")
#     --net=host --device /dev/gpiomem yashindane/smartcompass:v2 --ip="<IPV4-OF-PI>" --port=<UDP-PORT> 
#     --key="<GOOGLE-MAPS-API-KEY>" --keypad_rows="16,20,21,5" --keypad_cols="6,13,19,26" --motor_pins="17,18,27,22"
#     --ncei_key="<NCEI_API_KEY>"

# Author: Yash Indane <yashindane46@gmail.com>
# License: MIT


import time
import argparse
import logging
import RPi.GPIO as GPIO

from typing import List, Tuple
from src.inertial_mesurement_unit import IMU
from src.google_maps import PlacesAPI
from src.stepper_driver import Stepper
from src.compass_effect import compass_effect_driver
from src.declination_correction import compute_declination_angle



def processangle(*, place: str) -> int:
    """Calls the google_maps module to get the nearest place name and the final angle

    :param place: Place to look for (type str)
    :return: Final processed angle (type int)
    """

    places_api = PlacesAPI(API_KEY)
    # Get current IMU readings
    imu_reading: Tuple[float, str, str] = IMU(
        DEVICE_IPV4,
        DEVICE_UDP_PORT,
    ).get_imu_reading()

    dev_coordinates: Tuple[str, str] = imu_reading[1:]
    heading_angle: float = imu_reading[0]

    loc_coordinates: Tuple[float, float, str, str] = places_api.get_nearest_place(
        device_coordinates=dev_coordinates, place=place
    )

    BEARING_ANGLE: float = places_api.get_bearing_angle(
      a=(float(dev_coordinates[0]), float(dev_coordinates[1])), b=loc_coordinates[:2]
    )
  
    # Final angle calculation after adding magnetic declination correction
    FINAL_ANGLE: int = round(
        places_api.final_angle(bearing=BEARING_ANGLE, heading=heading_angle) \
        + compute_declination_angle(
            lat=float(dev_coordinates[0]),
            long=float(dev_coordinates[1]),
            key=NCEI_KEY,   
        )
        .get('declination_angle')
    )

    logging.info(f"place:{loc_coordinates[2]} {loc_coordinates[3]}")
    return FINAL_ANGLE


def setkeypad(*, rows: List[int], columns: List[int]) -> None:
    """Sets the RPI pins to interface the keypad

    :param rows: Keypad GPIO rows (type List[int])
    :param columns: Keypad GPIO rows (type List[int])
    :return: None
    """

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Set row pins as OUT
    for r_gpio in rows:
        GPIO.setup(r_gpio, GPIO.OUT)

    # Setting column pins as IN
    for c_gpio in columns:
        GPIO.setup(c_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def readline(*, line: int, characters: List[str], columns: List[int]) -> None:
    """Reads the keypad

    :param line: Line number (type int)
    :param characters: List of places (type List[str])
    :param columns: List of GPIO columns (type List[int])
    :return: None
    """

    global step_reset

    GPIO.output(line, GPIO.HIGH)

    for x in range(4):

        if(GPIO.input(columns[x]) == 1):
            place: str = characters[x]
            logging.info(place)
      
            if place == "Reset":
                stp.driver_stepper(angle=step_reset)
                step_reset = 0
        
            else:
                if step_reset == 0:
                    final_angle: int = processangle(place=place)
                    logging.info(final_angle)
                    stp.driver_stepper(angle=final_angle)
                    reset_angle_correction: int = compass_effect_driver(
                       HOST=DEVICE_IPV4,
                       PORT=DEVICE_UDP_PORT,
                       MOTOR_PINS=MOTOR_PINS,
                       keypad_lines=ROW_GPIOS,
                       keypad_columns=COLUMN_GPIOS,
                    ) 
                    step_reset = -final_angle + reset_angle_correction
                else:
                    logging.info("First press reset and then select next place!!")

    GPIO.output(line, GPIO.LOW)


def gpiocleanup():
    """Cleans up the GPIO pins before exiting"""
    
    all_gpios = []
    all_gpios.extend(ROW_GPIOS)
    all_gpios.extend(MOTOR_PINS)

    for g_pin in all_gpios:
        GPIO.output(g_pin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":

    # Set logging configuration
    logging.basicConfig(level=logging.NOTSET)

    # Parsing args
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, type=str, help="IPV4 of the RPI")
    parser.add_argument("--port", required=True, type=int, help="UDP port of the RPI")
    parser.add_argument("--key", required=True, type=str, help="Google Maps API key")
    parser.add_argument("--keypad_rows", required=True, type=str, help="Comma seperated GPIO pins for keypad rows")
    parser.add_argument("--keypad_cols", required=True, type=str, help="Comma seperated GPIO pins for keypad columns")
    parser.add_argument("--motor_pins", required=True, type=str, help="Comma seprated GPIO pins for stepper motor pins")
    parser.add_argument("--ncei_key", required=True, type=str, help="NCEI Key")

    args = parser.parse_args()
    DEVICE_IPV4 = args.ip
    DEVICE_UDP_PORT = args.port
    API_KEY = args.key
    NCEI_KEY = args.ncei_key

    # Setting up keypad
    ROW_GPIOS = [int(p) for p in args.keypad_rows.split(",")]
    COLUMN_GPIOS = [int(q) for q in args.keypad_cols.split(",")]
    KEYPAD_CHECK_INTERVAL = .25
    setkeypad(rows=ROW_GPIOS, columns=COLUMN_GPIOS)

    # Setting up stepper motor
    MOTOR_PINS = [int(h) for h in args.motor_pins.split(",")]
    stp = Stepper(motor_pins=MOTOR_PINS)
    stp.steppersetup()

    logging.info("Keypad & stepper setup sucessfull!!")

    # Stepper reset angle
    step_reset = 0

    places = [
        ["Automobile Service", "Hospital", "Police Station", "Petrol Pump"],
        ["Mall", "Pizza", "Bank", "Post Office"],
        ["Stadium", "Railway Station", "Airport", "Gym"],
        ["Hotel", "Restaurant", "School", "Reset"],
    ]

    try:
        while True:
            for i in range(len(places)):
                readline(line=ROW_GPIOS[i], characters=places[i], columns=COLUMN_GPIOS)
            time.sleep(KEYPAD_CHECK_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Closed")
        gpiocleanup()
