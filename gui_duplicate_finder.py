import os
import tkinter as tk
from tkinter import filedialog, messagebox
from duplicate_finder import find_duplicates
from output_duplicates import get_duplicates

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        db_path = "file_hashes.db"
        find_duplicates(directory, db_path)
        duplicates = get_duplicates(db_path)
        if duplicates:
            result = "\n".join([f"Hash: {file_hash}\n" + "\n".join([f" - {path}" for path in paths]) for file_hash, paths in duplicates.items()])
            messagebox.showinfo("Duplicates Found", result)
        else:
            messagebox.showinfo("No Duplicates", "No duplicate files found.")

def show_duplicates():
    db_path = "file_hashes.db"
    duplicates = get_duplicates(db_path)
    if duplicates:
        result = "\n".join([f"Hash: {file_hash}\n" + "\n".join([f" - {path}" for path in paths]) for file_hash, paths in duplicates.items()])
        messagebox.showinfo("Duplicates Found", result)
    else:
        messagebox.showinfo("No Duplicates", "No duplicate files found.")

def clean_up():
    db_path = "file_hashes.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        messagebox.showinfo("Cleanup", "Database has been deleted.")
    else:
        messagebox.showinfo("Cleanup", "No database found to delete.")

app = tk.Tk()
app.title("Duplicate Finder")

frame = tk.Frame(app, padx=10, pady=10)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Select a directory to find duplicate files:")
label.pack(pady=5)

select_button = tk.Button(frame, text="Select Directory", command=select_directory)
select_button.pack(pady=5)

show_button = tk.Button(frame, text="Show Duplicates", command=show_duplicates)
show_button.pack(pady=5)

clean_button = tk.Button(frame, text="Clean Up", command=clean_up)
clean_button.pack(pady=5)

app.mainloop()
