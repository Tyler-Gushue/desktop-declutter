import os
import shutil

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Media": [".mp4", ".mov", ".mkv", ".mp3", ".wav"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".iso"],
    "Code": [".py", ".html", ".css", ".js", ".json"]
}

def scan_and_clean(folder_path, delete_empty_var, delete_only_var, log_func=print):

    if not os.path.exists(folder_path):

        log_func("Selected path does not exist.")
        return

    log_func("...")

    item_count = 0
    moved_count = 0
    deleted_count = 0

    for item_name in os.listdir(folder_path):

        full_path = os.path.join(folder_path, item_name)

        if not delete_only_var:

            item_count += 1

            if os.path.isfile(full_path):

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

                item_count += 1

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

                log_func(f"Skipping file: {item_name}")

            elif os.path.isdir(full_path):

                item_count += 1

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
    log_func(f"Scan complete! Total items processed: {item_count} \nTotal items moved: {moved_count} \nTotal items deleted: {deleted_count}")