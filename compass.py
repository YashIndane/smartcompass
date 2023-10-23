#!/usr/bin/python3

"""
Main Smart Compass code.

 Usage -
   
   Pulling the container -
   $ sudo docker pull --platform linux/arm64/v8 docker.io/yashindane/smartcompass:latest

   Running the container -
   $ sudo docker run -it --platform linux/arm64/v8 --name smartcompass-con.$(date "+%Y.%m.%d-%H.%M.%S") --net=host --device /dev/gpiomem yashindane/smartcompass:v2 --ip="<IPV4-OF-PI>" --port=<UDP-PORT> --key="<GOOGLE-MAPS-API-KEY>" --keypad_rows="16,20,21,5" --keypad_cols="6,13,19,26" --motor_pins="17,18,27,22"

Author: Yash Indane <yashindane46@gmail.com>
License: MIT
"""


import RPi.GPIO as GPIO
import time
import argparse
import logging
import gmapintegration
import stepperdriver
import compasseffect


#Calls the gmapintefration module to get the nearest place name and the final angle
def processangle(PLACE:str) -> int:

  dev_coordinates = gmapintegration.get_device_coordinates(DEVICE_IPV4, DEVICE_UDP_PORT)
  loc_coordinates = gmapintegration.get_destination_coordinates(dev_coordinates, PLACE, API_KEY)
  BEARING_ANGLE = gmapintegration.get_bearing_angle((float(dev_coordinates[0]), float(dev_coordinates[1])), loc_coordinates[:2])
  HEADING_ANGLE = gmapintegration.get_heading(DEVICE_IPV4, DEVICE_UDP_PORT)
  FINAL_ANGLE = gmapintegration.final_angle(BEARING_ANGLE, HEADING_ANGLE)

  logging.info(f"place:{loc_coordinates[2]} {loc_coordinates[3]}")
  return FINAL_ANGLE


#Sets the RPI pins to interface the keypad
def setkeypad(rows:list, columns:list) -> None:

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)

  #Settins row pins as OUT
  for r_gpio in rows:
    GPIO.setup(r_gpio, GPIO.OUT)

  #Setting column pins as IN
  for c_gpio in columns:
    GPIO.setup(c_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


#Reads the keypad
def readline(line:int, characters:list, columns:list) -> None:

  global step_reset

  GPIO.output(line, GPIO.HIGH)

  for x in range(4):

    if(GPIO.input(columns[x]) == 1):

      place = characters[x]
      logging.info(place)
      
      if place == "Reset":
        stepperdriver.driver_stepper(step_reset, MOTOR_PINS)
        step_reset = 0
        
      else:

        if step_reset == 0:
          final_angle = processangle(place)
          logging.info(final_angle)
          stepperdriver.driver_stepper(final_angle, MOTOR_PINS)
          reset_angle_correction = compasseffect.compass_effect_driver(DEVICE_IPV4, DEVICE_UDP_PORT, MOTOR_PINS, ROW_GPIOS, COLUMN_GPIOS) 
          step_reset = -final_angle + reset_angle_correction
        else:
          logging.info("First press reset and then select next place!!")

  GPIO.output(line, GPIO.LOW)


#Cleans up the GPIO pins before exiting
def gpiocleanup():
    
    all_gpios = []
    all_gpios.extend(ROW_GPIOS)
    all_gpios.extend(MOTOR_PINS)

    for g_pin in all_gpios:
      GPIO.output(g_pin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":

  #Set logging configuration
  logging.basicConfig(level=logging.NOTSET)

  #Parsing args
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", required=True, type=str, help="IPV4 of the RPI")
  parser.add_argument("--port", required=True, type=int, help="UDP port of the RPI")
  parser.add_argument("--key", required=True, type=str, help="Google Maps API key")
  parser.add_argument("--keypad_rows", required=True, type=str, help="Comma seperated GPIO pins for keypad rows")
  parser.add_argument("--keypad_cols", required=True, type=str, help="Comma seperated GPIO pins for keypad columns")
  parser.add_argument("--motor_pins", required=True, type=str, help="Comma seprated GPIO pins for stepper motor pins")

  args = parser.parse_args()
  DEVICE_IPV4 = args.ip
  DEVICE_UDP_PORT = args.port
  API_KEY = args.key

  #Setting up keypad
  ROW_GPIOS = [int(p) for p in args.keypad_rows.split(",")]
  COLUMN_GPIOS = [int(q) for q in args.keypad_cols.split(",")]
  KEYPAD_CHECK_INTERVAL = 0.25
  setkeypad(ROW_GPIOS, COLUMN_GPIOS)

  #Setting up stepper motor
  MOTOR_PINS = [int(h) for h in args.motor_pins.split(",")]
  stepperdriver.steppersetup(MOTOR_PINS)

  logging.info("Keypad & stepper setup sucessfull!!")

  #Stepper reset angle
  step_reset = 0

  places = [
            ["Automobile Service", "Hospital", "Police Station", "Petrol Pump"],
            ["Mall", "Pizza", "Bank", "Post Office"],
            ["Stadium", "Railway Station", "Airport", "Gym"],
            ["Hotel", "Restaurant", "School", "Reset"]
  ]

  try:
    while True:

      for i in range(len(places)):
        readline(ROW_GPIOS[i], places[i], COLUMN_GPIOS)

      time.sleep(KEYPAD_CHECK_INTERVAL)

  except KeyboardInterrupt:
    logging.info("Closed")
    gpiocleanup()
