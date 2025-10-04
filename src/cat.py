import data_manager

# triggers a new run of the webscraper from the starting year until December 31st, 2024
def gatherAllData(startYear):
    return data_manager.generateFeatures(startYear)

# creates and saves a new model based on specified input data and maybe hyperparameters or something
# idk
def trainOnData(path):


    
    return 0

# the point of this method is to return model statistics such as loss and stuff but I fear that 
# may not be a fully reasonable task
def statistics(path): 
    return 0

# will probably scrape the days given race inputs and generate a prediction based on them
def predict(path): 
    return 0

# will call the gatherAllData method and then the trainOnData methods simultaneously to look
# really cool when it gear shifts in the terminal window
def createModel(path):
    return 0

#equivalent main function is down here
if __name__ == "__main__":
    # data_manager.generateFeatures(2022, LOAD_FILE="first_2024-2025_parse")
    # horses = data_manager.getFeatures("2022-2025")
    # algorithm.algorthm(horses)
    
    gatherAllData(1999)
    
