import csv
import os
from datetime import datetime



# saving all the input data 


def save_entry(mood, energy, note):

    filename = "data/checkin.csv"           # create a filename "checkin.csv" in the "data" folder
    file_exists = os.path.isfile(filename)  # if data folder doesn't exist make it with os.makedirs


    with open(filename, "a", newline="") as f: 
        writer = csv.writer(f)
        if not file_exists: # if the file doesn't exist, write the header
            writer.writerow(["timestamp", "mood", "energy", "note"]) 
            # write the header to the csv file 
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mood, energy, note]) 
        # write the timestamp, mood, and energy to the csv file


