
# filepath: /home/echeadle/Aug_2024/Projects/dup_files/src/main.py
from duplicate_finder import find_duplicates

if __name__ == "__main__":
    directory = "/path/to/directory"
    db_path = "/path/to/database.db"
    find_duplicates(directory, db_path)