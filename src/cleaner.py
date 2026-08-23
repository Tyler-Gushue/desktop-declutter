import os

def scan_and_clean(folder_path, log_func=print):

    if not os.path.exists(folder_path):
        return

    global file_count

    file_count = 0

    for item_name in os.listdir(folder_path):

        full_path = os.path.join(folder_path, item_name)

        if os.path.isfile(full_path):
            file_count += 1
            log_func(f"Found file: {item_name}")
        elif os.path.isdir(full_path):
            log_func(f"Skipping folder: {item_name}")

    log_func(f"Scan complete. Total files scanned: {file_count}")