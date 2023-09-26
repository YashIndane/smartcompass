import RPi.GPIO as GPIO
import time
import argparse
import gmapintegration



def processangle(DEVICE_IPV4:str, DEVICE_UDP_PORT:int, API_KEY:str, PLACE:str) -> int:

    dev_coordinates = gmapintegration.get_device_coordinates(DEVICE_IPV4, DEVICE_UDP_PORT)
    loc_coordinates = gmapintegration.get_destination_coordinates(dev_coordinates, PLACE, API_KEY)
    BEARING_ANGLE = gmapintegration.get_bearing_angle((float(dev_coordinates[0]), float(dev_coordinates[1])), loc_coordinates[:2])
    HEADING_ANGLE = gmapintegration.get_heading(DEVICE_IPV4, DEVICE_UDP_PORT)
    FINAL_ANGLE = gmapintegration.final_angle(BEARING_ANGLE, HEADING_ANGLE)

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

    GPIO.output(line, GPIO.HIGH)

    if(GPIO.input(columns[0]) == 1):

        place = characters[0]
        print(place)
        #final_angle = processangle()

    if(GPIO.input(columns[1]) == 1):

        place = characters[1]
        print(place)
        #final_angle = processangle()

    if(GPIO.input(columns[2]) == 1):

        place = characters[2]
        print(place)
        #final_angle = processangle()

    if(GPIO.input(columns[3]) == 1):

        place = characters[3]
        print(place)
        #final_angle = processangle()


    GPIO.output(line, GPIO.LOW)


if __name__=="__main__":

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

  try:
    while True:
      readline(ROW_GPIOS[0], ["Automobile Service", "Hospital", "Police Station", "Petrol Pump"], COLUMN_GPIOS)
      readline(ROW_GPIOS[1], ["Mall", "Pizza", "Bank", "Post Office"], COLUMN_GPIOS)
      readline(ROW_GPIOS[2], ["Stadium", "Railway Station", "Airport", "Gym"], COLUMN_GPIOS)
      readline(ROW_GPIOS[3], ["Hotel", "Restaurant", "School", "Reset"], COLUMN_GPIOS)
      time.sleep(KEYPAD_CHECK_INTERVAL)

  except KeyboardInterrupt:
    print("Closed")
