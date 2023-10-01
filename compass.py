import RPi.GPIO as GPIO
import time
import argparse
import gmapintegration
import stepperdriver
import compasseffect

#sudo python3 compass.py --port=<UDP-PORT> --ip="<IPV4>" --key="<GMAP-API-KEY>"


def processangle(PLACE:str) -> int:

  dev_coordinates = gmapintegration.get_device_coordinates(DEVICE_IPV4, DEVICE_UDP_PORT)
  loc_coordinates = gmapintegration.get_destination_coordinates(dev_coordinates, PLACE, API_KEY)
  BEARING_ANGLE = gmapintegration.get_bearing_angle((float(dev_coordinates[0]), float(dev_coordinates[1])), loc_coordinates[:2])
  HEADING_ANGLE = gmapintegration.get_heading(DEVICE_IPV4, DEVICE_UDP_PORT)
  FINAL_ANGLE = gmapintegration.final_angle(BEARING_ANGLE, HEADING_ANGLE)

  print(f"place:{loc_coordinates[2]} {loc_coordinates[3]}")
  return FINAL_ANGLE


def setkeypad(rows:list, columns:list) -> None:

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)

  #Settins row pins as OUT
  for r_gpio in rows:
    GPIO.setup(r_gpio, GPIO.OUT)

  #Setting column pins as IN
  for c_gpio in columns:
    GPIO.setup(c_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def readline(line:int, characters:list, columns:list) -> None:

  global step_reset

  GPIO.output(line, GPIO.HIGH)

  for x in range(4):

    if(GPIO.input(columns[x]) == 1):

      place = characters[x]
      print(place)
      
      if place == "Reset":
        stepperdriver.driver_stepper(step_reset, MOTOR_PINS)
        step_reset = 0
        
      else:

        if step_reset == 0:
          final_angle = processangle(place)
          print(final_angle)
          stepperdriver.driver_stepper(final_angle, MOTOR_PINS)
          #compasseffect.compass_effect_driver(DEVICE_IPV4, DEVICE_UDP_PORT, MOTOR_PINS) 
          step_reset = -final_angle
        else:
          print("First press reset and then select next place!!")

  GPIO.output(line, GPIO.LOW)

def gpiocleanup():
    
    all_gpios = []
    all_gpios.extend(ROW_GPIOS)
    all_gpios.extend(MOTOR_PINS)

    for g_pin in all_gpios:
      GPIO.output(g_pin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":

  #Parsing args
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", required=True, type=str, help="IPV4 of the RPI")
  parser.add_argument("--port", required=True, type=int, help="UDP port of the RPI")
  parser.add_argument("--key", required=True, type=str, help="Google Maps API key")

  args = parser.parse_args()
  DEVICE_IPV4 = args.ip
  DEVICE_UDP_PORT = args.port
  API_KEY = args.key

  #Setting up keypad
  ROW_GPIOS = [16, 20, 21, 5]
  COLUMN_GPIOS = [6, 13, 19, 26]
  KEYPAD_CHECK_INTERVAL = 0.25
  setkeypad(ROW_GPIOS, COLUMN_GPIOS)

  #Setting up stepper motor
  MOTOR_PINS = [17, 18, 27, 22]
  stepperdriver.steppersetup(MOTOR_PINS)

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
    print("Closed")
    gpiocleanup()
