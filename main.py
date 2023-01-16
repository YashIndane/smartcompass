from selenium import webdriver
import time
import argparse
import math
import socket
import logging



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
        data = str(data).split(" ")
        
        if len(data) >= 17:
            heading = data[-5]

            if all(["." in heading, "-" not in heading, heading[:3] != "0.0"]):
                sock.close()
                return float(heading[:-1])

    
    
def get_destination_coordinates() -> tuple:

    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)

    parser = argparse.ArgumentParser()
    parser.add_argument("--place", required=True)
    args = parser.parse_args()
    place = args.place

    place = place.replace(" ", "+")
    driver.get(f"https://google.co.in/search?q=nearest+{place}+directions")

    time.sleep(15)

    button = driver.find_element_by_xpath("/html/body/div[7]/div/div[11]/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div/div/div[4]/div[2]/a/img")

    driver.execute_script("arguments[0].click();", button)

    time.sleep(5)

    URL = driver.current_url
    inds = URL.index("2m2!1d")
    inde = URL.index("!3e0")
    lon, lat = URL[inds+6:inde].split("!2d")
    place_name = URL.split("/")[6].replace("+", " ")
    return (float(lat), float(lon), place_name)


def get_device_coordinates(device_ip:str, udp_port:int) -> tuple:
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((device_ip, udp_port))
    device_coordinates = ()

    while len(device_coordinates) == 0:
        BUFFER_SIZE = 1024
        data, address = sock.recvfrom(BUFFER_SIZE)
        temp = str(data).split(" ")
        
        if len(temp) >= 40:
            device_coordinates = (
                    float(temp[3].replace(",", " ")),
                    float(temp[5].replace(",", " "))
            )
    
    sock.close()

    return device_coordinates


if __name__ == "__main__":
    
    #Setting logging configuration
    logging.basicConfig(level=logging.NOTSET)

    DEVICE_IPV4 = "192.168.29.254"
    DEVICE_UDP_PORT = 1008

    logging.info("Fetching device coordinates...")
    dev_coordinates = get_device_coordinates(DEVICE_IPV4, DEVICE_UDP_PORT)
    logging.info(dev_coordinates)
    
    logging.info("Finding nearest location...")
    loc_coordinates = get_destination_coordinates()
    logging.info(loc_coordinates[:2])
    logging.info(loc_coordinates[2])
   
    BEARING_ANGLE = get_bearing_angle(dev_coordinates, loc_coordinates[:2])
    logging.info(f"Bearing Angle:{BEARING_ANGLE}")

    HEADING_ANGLE = get_heading(DEVICE_IPV4, DEVICE_UDP_PORT)
    logging.info(f"Heading Angle:{HEADING_ANGLE}")

    FINAL_ANGLE = final_angle(BEARING_ANGLE, HEADING_ANGLE)
    logging.info(f"Final Angle:{FINAL_ANGLE}")

