from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import shutil
import numpy as np
import time
import pandas
import json
from concurrent.futures import ThreadPoolExecutor
import os
import traceback

# CONFIG 
CHROMEDRIVER_PATH = shutil.which("chromedriver")
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless=new")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")
CHROME_OPTIONS.add_argument("--disable-gpu")
SERVICE = Service(CHROMEDRIVER_PATH)
PROGRESS_PATH = "/home/devin/projects/cat/saved-data/progress.json"
INSTANTIATION_PATH = "/home/devin/projects/cat/saved-data/instantiation.json"
MAX_LENGTH = 20

# amount of cpus to pick from. Decides how many webdrives to keep open and how many threads to manage
POOL_SIZE = os.cpu_count()

# CONSTANTS
RESTART_DRIVER_INTERVAL = 100

# Global pool of drivers
_drivers = []
_next_driver_index = 0

# returns a rotating selection of drivers from the pool
def get_driver():
    global _drivers, _next_driver_index
    if not _drivers:
        raise RuntimeError("Driver pool empty")
    
    driver = _drivers[_next_driver_index]
    _next_driver_index = (_next_driver_index + 1) % len(_drivers)
    return driver

# quits out of all the drivers at once to avoid memory leaks
def quit_all_drivers():
    global _drivers
    for d in _drivers:
        d.quit()
    _drivers = []

# generates all drivers to be used at the beginning of the scripting sequence
def init_drivers(driver_count=1):
    quit_all_drivers()
    global _drivers, _next_driver_index
    _drivers = [webdriver.Chrome(service=SERVICE, options=CHROME_OPTIONS) for i in range(driver_count)]
    _next_driver_index = 0

# Scrapes race hyperlinks from a daily results page
def getFullResultHyperlinks(WebURL):
    driver = get_driver()
    driver.get(WebURL)

    elements = driver.find_elements(
        "css selector",
        "a.rp-raceCourse__panel__race__info__buttons__link.js-popupLink"
    )
    return [e.get_attribute("href") for e in elements]

# Extracts data for a single horse row
def parseHorse(row):
    def safe_text(selector, attr="text"):
        try:
            el = row.find_element("css selector", selector)
            return el.get_attribute(attr) if attr != "text" else el.text
        except:
            return ""
    
    pos = safe_text("[data-test-selector='text-horsePosition']").rstrip()
    draw = '0'

    for i in range(2, len(pos)):
        if (pos[i] == '('):
            draw = pos[i + 1 : pos.find(')' , i + 2)]
            pos = pos[ : i - 1]

            break

    age = safe_text("[data-test-selector='horse-age']")
    orating = safe_text("[data-ending='OR']")
    ts = safe_text("[data-test-selector='full-result-topspeed']")
    rpr = safe_text("[data-test-selector='full-result-rpr']")
    st = safe_text("[data-test-selector='horse-weight-st']")
    lb = safe_text("[data-test-selector='horse-weight-lb']")

    horse = [draw, age, orating, ts, rpr, st, lb, pos]
    for i in range(len(horse)):
        if (not horse[i].isdigit()):
            horse[i] = 0
    return list(map(int, horse))

# Parses a single race
def parseRace(hyperlink):
    driver = get_driver()
    driver.get(hyperlink)
    rows = driver.find_elements("css selector", "tr.rp-horseTable__mainRow")
    return [parseHorse(row) for row in rows]

# Parses all races for a given day
def parseDay(WebURL):
    links = getFullResultHyperlinks(WebURL)
    results = []

    if links:
        # Parallel scrape races
        with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
            results = list(executor.map(parseRace, links))

    dayHorses = np.vstack(results)

    return dayHorses

def updateDog(thingToSave: dict, filename=PROGRESS_PATH):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        data["data"].insert(0, thingToSave)
        data["data"] = data["data"][:MAX_LENGTH]
    except Exception:
        data = {"data": [thingToSave]} 

    # Write the updated list back to the same JSON file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


# Parses entire histories worth of races
def parseRacingPostHistory(
    YEAR_LIMIT=2024, MONTH_LIMIT=12, DAY_LIMIT=31,
    START_YEAR=1988, START_MONTH=1, START_DAY=1):
    
    parseRange = pandas.date_range(start=f"{START_YEAR:04d}-{START_MONTH:02d}-{START_DAY:02d}", 
                                   end=f"{YEAR_LIMIT:04d}-{MONTH_LIMIT:02d}-{DAY_LIMIT:02d}", freq="D")
    init_drivers(driver_count=POOL_SIZE)

    allHorses = []
    yearsHorses = []
    dayCount = 0

    with open(INSTANTIATION_PATH, "w") as file:
                json.dump({ "startYear": START_YEAR, 
                            "startMonth": START_MONTH,
                            "startDay": START_DAY, 
                            "endYear": YEAR_LIMIT, 
                            "endMonth": MONTH_LIMIT,
                            "endDay": DAY_LIMIT}, file)

    for dayPeriod in parseRange:
        # every new year create a save state
        if (dayPeriod.day == 1 and dayPeriod.month == 1 and dayPeriod.year != START_YEAR):
            year = np.vstack(yearsHorses)

            if len(allHorses) == 0:
                allHorses = year
            else:
                allHorses = np.vstack((allHorses, year))

            np.save("../saved-data/temp/" + str(dayPeriod.year - 1) + ".npy", year)
            yearsHorses = []


        startTime = time.time()

        dateString = f"{dayPeriod.year:04d}-{dayPeriod.month:02d}-{dayPeriod.day:02d}"
        url = f"https://www.racingpost.com/results/{dateString}"

        # parse races for the day
        try:
            dayHorses = parseDay(url)
            yearsHorses.append(dayHorses)
            updateDog({"active": True, 
                        "year": dayPeriod.year, 
                        "month": dayPeriod.month,
                        "day": dayPeriod.day,
                        "horses": len(dayHorses),
                        "time": round(time.time() - startTime)})
                            
            print(f"Scraped {len(dayHorses)} horses for {dateString}")

        except Exception as e:
            print(f"Error scraping {dateString}: {e}")

        print(f"Parsing {dateString} took:", time.time() - startTime, "seconds")

        # periodically restart driver
        dayCount += 1
        if dayCount % RESTART_DRIVER_INTERVAL == 0:
            if _drivers:
                print("Restarting Selenium drivers to free memory...")
                quit_all_drivers()
                init_drivers(driver_count=POOL_SIZE)

    year = np.vstack(yearsHorses)
    if len(allHorses) == 0:
        allHorses = year
    else:
        allHorses = np.vstack((allHorses, year))
    np.save("../saved-data/temp/" + str(YEAR_LIMIT) + ".npy", year)

    quit_all_drivers()

    return allHorses

# for building simple test executions
if __name__ == "__main__":
    try: 
        parseRacingPostHistory(START_YEAR=2000, START_MONTH=1, START_DAY=1)
    except:
        traceback.print_exc()