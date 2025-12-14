#!/usr/bin/python3

# Module to interact with Google Maps Services

import googlemaps
import math
from typing import Tuple, Dict

class PlacesAPI:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self.gmaps_client = googlemaps.Client(key=api_key)


    def get_nearest_place(
        self,
        *,
        device_coordinates: Tuple[str, str],
        place: str,
        ) -> Tuple[float, float, str, str]:
        """Gets nearest place details
        
        :param device_coordinates: Latitude and longitude of the Device (type Tuple[str, str])
        :place: Places to search (type str)
        :return: Nearest place details (type Tuple[float, float, str, str])
        """

        result: Dict = self.gmaps_client.places_nearby(
            location=','.join(device_coordinates),
            keyword=place,
            rank_by='distance',
        )['results'][0]

        return (
            result['geometry']['location']['lat'],
            result['geometry']['location']['lng'],
            result['name'],
            result['vicinity'],
        )


    @staticmethod
    def get_bearing_angle(
        *,
        a: Tuple[float, float],
        b: Tuple[float, float],
    ) -> float:
        """Returns the angle between north-south line and the 
           line connecting current and desired location

        :param a: Latitude and longitude of device (type Tuple[float, float])
        :param b: Latitude and longitude of desired place (type Tuple[float, float])
        :return: Bearing angle (type float)
        """
    
        a, b = [math.radians(x) for x in a], [math.radians(x) for x in b]
        diffLong = b[1] - a[1]

        _X: float = (math.cos(b[0]) * math.sin(diffLong))
        _Y: float = (math.cos(a[0]) * math.sin(b[0])) \
                    - (math.sin(a[0]) * math.cos(b[0]) * math.cos(diffLong))

        return math.degrees(math.atan2(_X, _Y))


    @staticmethod
    def final_angle(*, bearing: float, heading: float) -> float:
        """Final angle

        :param bearing: Bearing angle (type float)
        :param heading: Heading angle (type float)
        :return: None
        """
        f_angle = bearing - heading
        return f_angle+360 if f_angle<-180 else f_angle
