import os

def scan_and_clean(folder_path):

    if not os.path.exists(folder_path):
        return

    for item_name in os.listdir(folder_path):

        full_path = os.path.join(folder_path, item_name)

        if os.path.isfile(full_path):
            print(f"Found file: {item_name}")
        elif os.path.isdir(full_path):
            print(f"Skipping folder: {item_name}")