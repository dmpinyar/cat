import webscraper
import numpy as np

# simply gets the data from the webscraper
def getData(startYear, endYear=2025, endMonth=12, endDay=31):
    return webscraper.parseRacingPostHistory(START_YEAR=startYear, YEAR_LIMIT=endYear, MONTH_LIMIT=endMonth, DAY_LIMIT=endDay)

# cleans the data from the webscraper
# as of right now I like what the data looks like
# this will just remove null entries (brought about when a horse falls 
# or something, should probably include,
# but it happens rare enough for me not want to predict it)
# this will also randomize the indicies of the array
def cleanData(ADT):
    mask = ADT[:, 7] != 0
    ADT = ADT[mask]
    
    np.random.shuffle(ADT)
    return ADT

# saves the CLEANED data to a file
def saveData(ADT, filename):
    np.save("../saved-data/" + filename + ".npy", ADT)

# calls the previous three functions to get, clean, and save the data
# has additional functionality for calling already collected
# yearly saved data (constructed around crashes and errors)
def generateFeatures(startYear, endYear=2025, LOAD_TEMP=False, LOAD_FILE=None):
    if (LOAD_TEMP == True):
        results = []
        for year in range(startYear, endYear):
            try:
                fileLoad = np.load("../saved-data/temp/" + str(year) + ".npy")
                results.append(fileLoad)
            except:
                results.append(getData(endYear=year + 1, startYear=year))
        horses = np.vstack(results)
    else:
        if (LOAD_FILE != None):
            horses = np.load("../saved-data/" + LOAD_FILE + ".npy")
        else:
            horses = getData(startYear, endYear)
        
    clean = cleanData(horses)
    saveData(clean, str(startYear) + "-" + str(endYear))

    return clean

# gets the saved features from the file
def getFeatures(filename):
    return np.load("../saved-data/" + filename + ".npy")

# gets the weights array from storage
def getWeights(name):
    return 0

# saves the weights array to storage
def saveWeights(name):
    return 0

if __name__ == "__main__":
    print("1")