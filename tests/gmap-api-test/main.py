import argparse
import googlemaps
import math
import socket
import logging

#sudo python3 main.py --ip="<IPV4-OF-RPI>" --port="<UDP-PORT-OF-RPI>" --place="<PLACE>" --key="<GMAP-API-KEY>"


def final_angle(bearing:float, heading:float) -> int:

    f_angle = round(bearing-heading)
    return f_angle+360 if f_angle<-180 else f_angle


def get_bearing_angle(a:tuple, b:tuple) -> float:
    
    a = [math.radians(x) for x in a]
    b = [math.radians(x) for x in b]
    diffLong = b[1]-a[1]
    X = (math.cos(b[0]))*(math.sin(diffLong))
    Y = math.cos(a[0])*math.sin(b[0])-math.sin(a[0])*math.cos(b[0])*math.cos(diffLong)
    B = math.atan2(X, Y)
    BEARING_ANGLE = math.degrees(B)
    return BEARING_ANGLE


def get_heading(device_ip:str, udp_port:int) -> float:

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((device_ip, udp_port))
    
    
    while True:

        BUFFER_SIZE = 1024
        data, address = sock.recvfrom(BUFFER_SIZE)
        data = str(data)[2:].split(',')
        X_ROT = float(data[0])
        sock.close()
        return X_ROT

    
def get_destination_coordinates(loc:tuple, place:str, api_key:str) -> tuple:

    loc_string = ",".join(loc)

    gmaps_client = googlemaps.Client(key=api_key)
    place_result = gmaps_client.places_nearby(location=loc_string, keyword=place, rank_by="distance")

    nearest_place = place_result["results"][0]
    nearest_place_lat = nearest_place["geometry"]["location"]["lat"]
    nearest_place_lng = nearest_place["geometry"]["location"]["lng"]
    nearest_place_name = nearest_place["name"]
    nearest_place_vicinity = nearest_place["vicinity"]

    return (nearest_place_lat, nearest_place_lng, nearest_place_name, nearest_place_vicinity)



def get_device_coordinates(device_ip:str, udp_port:int) -> tuple:
    
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((device_ip, udp_port))

    while True:
      BUFFER_SIZE = 1024
      data, address = sock.recvfrom(BUFFER_SIZE)
      data = str(data)[2:].split(',')
      lat = data[3]
      lng = data[4]
      sock.close()
      return (lat, lng)


if __name__ == "__main__":
    
    #Setting logging configuration
    logging.basicConfig(level=logging.NOTSET)

    #Parsing args
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, type=str, help="IPv4 of the RPI")
    parser.add_argument("--port", required=True, type=int, help="UDP port of RPI")
    parser.add_argument("--place", required=True, type=str, help="PLace you are looking for")
    parser.add_argument("--key", required=True, type=str, help="Google Maps API KEY")

    args = parser.parse_args()
    DEVICE_IPV4 = args.ip
    DEVICE_UDP_PORT = args.port
    PLACE = args.place
    API_KEY = args.key


    logging.info("Fetching device coordinates...")
    dev_coordinates = get_device_coordinates(DEVICE_IPV4, DEVICE_UDP_PORT)
    logging.info(dev_coordinates)
    
    logging.info("Finding nearest location...")
    loc_coordinates = get_destination_coordinates(dev_coordinates, PLACE, API_KEY)
    logging.info(f"LAT:{loc_coordinates[0]}")
    logging.info(f"LNG:{loc_coordinates[1]}")
    logging.info(f"Place:{loc_coordinates[2]} {loc_coordinates[3]}")
    
   
    BEARING_ANGLE = get_bearing_angle((float(dev_coordinates[0]), float(dev_coordinates[1])), loc_coordinates[:2])
    logging.info(f"Bearing Angle:{BEARING_ANGLE}")

    HEADING_ANGLE = get_heading(DEVICE_IPV4, DEVICE_UDP_PORT)
    logging.info(f"Heading Angle:{HEADING_ANGLE}")

    FINAL_ANGLE = final_angle(BEARING_ANGLE, HEADING_ANGLE)
    logging.info(f"Final Angle:{FINAL_ANGLE}")

