import os
import shutil
import hashlib

# Categories that . file types get stored into

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Media": [".mp4", ".mov", ".mkv", ".mp3", ".wav"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".iso"],
    "Code": [".py", ".html", ".css", ".js", ".json"]
}

# Function for getting hash of a file

def get_file_hash (filepath):

    hasher = hashlib.md5()

    try:

        with open (filepath, "rb") as f:

            while chunk := f.read(8192):

                hasher.update(chunk)

        return hasher.hexdigest()
    
    except (PermissionError, OSError):

        return None

# Function for scanning directory

def scan_and_clean(folder_path, delete_empty_var, delete_only_var, delete_duplicates_var, log_func=print, progress_callback=None):

    if not os.path.exists(folder_path):

        log_func("Selected path does not exist.")
        return

    seen_hashes = {}

    log_func("...")

    item_count = 0
    moved_count = 0
    deleted_count = 0

    items = os.listdir(folder_path)
    total_items = len(items)

    for index, item_name in enumerate(items, start=1):

        full_path = os.path.join(folder_path, item_name)

        if progress_callback:

            progress_callback(index, total_items)

        if not delete_only_var:

            item_count += 1

            if os.path.isfile(full_path):

                if delete_duplicates_var :

                    file_hash = get_file_hash(full_path)

                    if file_hash:
                            
                            if file_hash in seen_hashes:

                                try:

                                    os.remove(full_path)
                                    deleted_count += 1
                                    log_func(f"Deleted duplicate file: {item_name}")
                                    continue
                                
                                except OSError as e:

                                    log_func(f"Could not delete duplicate {item_name}: {e}")

                            else:

                                seen_hashes[file_hash] = full_path

                _, ext = os.path.splitext(item_name)
                ext = ext.lower()

                destination_category = "Other"

                for category, extensions in CATEGORIES.items():

                    if ext in extensions:

                        destination_category = category
                        break

                target_folder_path = os.path.join(folder_path, destination_category)
                os.makedirs(target_folder_path, exist_ok=True)

                target_file_path = os.path.join(target_folder_path, item_name)

                if not os.path.exists(target_file_path):

                    shutil.move(full_path, target_file_path)
                    moved_count += 1
                    log_func(f"Moved: {item_name} -> {destination_category}/")

                else:

                    log_func(f"Skipped duplicate: {item_name}")

            elif os.path.isdir(full_path):

                if delete_empty_var:

                    try:

                        if not os.listdir(full_path):

                            deleted_count += 1
                            os.rmdir(full_path)
                            log_func(f"Folder is empty.  Deleting Folder: {item_name}")

                        else:

                            log_func(f"Folder isn't empty.  Skipping Folder: {item_name}")

                    except OSError as e:

                        log_func(f"Could not delete folder {item_name}: {e}")
                    
                else:

                    log_func(f"Skipping folder: {item_name}")
                    
        else:

            item_count += 1

            if os.path.isfile(full_path):

                if delete_duplicates_var :

                    file_hash = get_file_hash(full_path)

                    if file_hash:
                            
                            if file_hash in seen_hashes:

                                try:

                                    os.remove(full_path)
                                    deleted_count += 1
                                    log_func(f"Deleted duplicate file: {item_name}")
                                    continue

                                except OSError as e:

                                    log_func(f"Could not delete duplicate {item_name}: {e}")

                            else:

                                seen_hashes[file_hash] = full_path

            elif os.path.isdir(full_path):

                if delete_empty_var:

                    try:

                        if not os.listdir(full_path):

                            deleted_count += 1
                            os.rmdir(full_path)
                            log_func(f"Folder is empty.  Deleting Folder: {item_name}")

                        else:

                            log_func(f"Folder isn't empty.  Skipping Folder: {item_name}")

                    except OSError as e:

                        log_func(f"Could not delete folder {item_name}: {e}")
                    
                else:

                    log_func(f"Skipping folder: {item_name}")

    log_func("...")
    log_func(f"Scan complete! \nTotal items processed: {item_count} \nTotal items moved: {moved_count} \nTotal items deleted: {deleted_count}")