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

app = tk.Tk()
app.title("Duplicate Finder")

frame = tk.Frame(app, padx=10, pady=10)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Select a directory to find duplicate files:")
label.pack(pady=5)

select_button = tk.Button(frame, text="Select Directory", command=select_directory)
select_button.pack(pady=5)

app.mainloop()
