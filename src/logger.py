from .input_handler import get_mood, get_energy, get_note
from .file_handler import save_entry

if __name__ == "__main__":
    mood = get_mood()
    energy = get_energy()
    note = get_note()
    save_entry(mood, energy, note)
    print(f"Entry saved: Mood={mood}, Energy={energy}, Note={note}")
