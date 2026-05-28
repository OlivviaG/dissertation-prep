import csv
from fileinput import filename
import os
from datetime import datetime


# mood tracker logger
def get_mood():
    mood = input("Mood score (1-10): ")
    return int(mood)

def get_energy():
    energy = input("Energy score (1-10): ")
    return int(energy)

def get_note():
    note = input("Any notes for today (press enter to skip): ")
    return note


def save_entry(mood, energy, note):

    filename = "data/checkin.csv"           # create a filename "checkin.csv" in the "data" folder
    file_exists = os.path.isfile(filename)  # if data folder doesn't exist make it with os.makedirs


    with open(filename, "a", newline="") as f: 
        writer = csv.writer(f)
        if not file_exists: # if the file doesn't exist, write the header
            writer.writerow(["timestamp", "mood", "energy", "note"]) # write the header to the csv file 
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mood, energy, note]) # write the timestamp, mood, and energy to the csv file

if __name__ == "__main__":
    mood = get_mood()           # get user input for mood
    energy = get_energy()       # get user input for energy
    note = get_note()           # get user input for notes
    save_entry(mood, energy, note)    # save the entry to the csv file
    print(f"Entry saved: Mood={mood}, Energy={energy}, Note={note}") # print a confirmation message with the saved entry    