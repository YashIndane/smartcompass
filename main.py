from selenium import webdriver
import time
import argparse

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
parser.add_argument("--x", required=True)
args = parser.parse_args()
place = args.x

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
print(lat, lon, "\n", place_name)
