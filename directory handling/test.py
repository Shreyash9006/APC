import os
import shutil

folder = r"D:\Shreyash\lab\directory handling\files"

for file in os.listdir(folder):
    print(file)

    file_path = os.path.join(folder, file)

    # Skip folders
    if os.path.isdir(file_path):
        continue

    extension = os.path.splitext(file)[1].lower()

    if extension in [".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx"]:
        new_folder = "Documents"

    elif extension in [".jpg", ".jpeg", ".png", ".gif"]:
        new_folder = "Images"

    elif extension in [".mp3", ".wav"]:
        new_folder = "Audio"

    elif extension in [".mp4", ".mkv", ".avi"]:
        new_folder = "Videos"

    else:
        new_folder = "Others"

    # Create folder if it doesn't exist
    #folder_path = os.path.join(folder, new_folder)
    #os.makedirs(folder_path, exist_ok=True)

    # Move file
    #shutil.move(file_path, os.path.join(folder_path, file))

print("Files organized successfully!")