#!/usr/bin/python3


"""
Google Maps Integration module. This uses Google Maps API.
"""


import argparse
import googlemaps
import math
import socket


#Returns the final angle from bearing and heading angles
def final_angle(bearing:float, heading:float) -> int:

    f_angle = round(bearing-heading)
    return f_angle+360 if f_angle<-180 else f_angle


#Returns the angle between north-south line and the line connecting current and desired location
def get_bearing_angle(a:tuple, b:tuple) -> float:
    
    a = [math.radians(x) for x in a]
    b = [math.radians(x) for x in b]
    diffLong = b[1]-a[1]
    X = (math.cos(b[0]))*(math.sin(diffLong))
    Y = math.cos(a[0])*math.sin(b[0])-math.sin(a[0])*math.cos(b[0])*math.cos(diffLong)
    B = math.atan2(X, Y)
    BEARING_ANGLE = math.degrees(B)
    return BEARING_ANGLE


#Returns the current device heading
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


#Returns the desired closest location coordinates and other details 
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


#Returns the current device coordinates
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
