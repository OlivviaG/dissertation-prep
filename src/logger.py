import csv
from fileinput import filename
import os
from datetime import datetime


# mood tracker logger
def get_mood():
    mood = input("How are you feeling today? (1-10): ")
    return int(mood)

def save_entry(mood):
    filename = "data/checkin.csv"           # create a filename "checkin.csv" in the "data" folder
    file_exists = os.path.isfile(filename)  # if data folder doesn't exist make it with os.makedirs

    with open(filename, "a", newline="") as f: 
        writer = csv.writer(f)
        if not file_exists: # if the file doesn't exist, write the header
            writer.writerow(["timestamp", "mood"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mood]) # write the timestamp and mood to the csv file

    if __name__ == "__main__":
        mood = get_mood()           # get user input for mood
        save_entry(mood)            # save the mood entry to the csv file