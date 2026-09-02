import os
import shutil
import hashlib

# Default fallback categories in case no preset is passed
DEFAULT_PRESET_DATA = {
    "sort_uncategorized_to_other": True,
    "categories": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Media": [".mp4", ".mov", ".mkv", ".mp3", ".wav"],
        "Installers": [".exe", ".msi", ".dmg", ".pkg", ".iso"],
        "Code": [".py", ".html", ".css", ".js", ".json"]
    }
}

def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None

def scan_and_clean(
    folder_path,
    delete_empty_var,
    delete_only_var,
    delete_duplicates_var,
    preset_data=None,
    log_func=print,
    progress_callback=None
):
    if not os.path.exists(folder_path):
        log_func("Selected path does not exist.")
        return []

    # Use selected preset rules or default fallback
    current_preset = preset_data or DEFAULT_PRESET_DATA
    categories_map = current_preset.get("categories", {})
    sort_to_other = current_preset.get("sort_uncategorized_to_other", True)

    seen_hashes = {}
    log_func("...")

    item_count = 0
    moved_count = 0
    deleted_count = 0

    items = os.listdir(folder_path)
    total_items = len(items)
    moved_history = []

    for index, item_name in enumerate(items, start=1):
        full_path = os.path.join(folder_path, item_name)

        if progress_callback:
            progress_callback(index, total_items)

        item_count += 1

        # --- Handle Files ---
        if os.path.isfile(full_path):
            # Duplicate check
            if delete_duplicates_var:
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

            # Skip sorting step if running in Delete Only Mode
            if delete_only_var:
                continue

            _, ext = os.path.splitext(item_name)
            ext = ext.lower()

            destination_category = None

            # Match extension against current preset's categories
            for category, extensions in categories_map.items():
                if ext in extensions:
                    destination_category = category
                    break

            # If unmapped, check if sort to 'Other' is enabled
            if not destination_category:
                if sort_to_other:
                    destination_category = "Other"
                else:
                    log_func(f"Skipping uncategorized file: {item_name}")
                    continue

            target_folder_path = os.path.join(folder_path, destination_category)
            os.makedirs(target_folder_path, exist_ok=True)

            target_file_path = os.path.join(target_folder_path, item_name)

            if not os.path.exists(target_file_path):
                try:
                    shutil.move(full_path, target_file_path)
                    moved_history.append((full_path, target_file_path))
                    moved_count += 1
                    log_func(f"Moved: {item_name} -> {destination_category}/")
                except OSError as e:
                    log_func(f"Could not move {item_name}: {e}")
            else:
                log_func(f"Skipped duplicate filename: {item_name}")

        # --- Handle Directories ---
        elif os.path.isdir(full_path):
            if delete_empty_var:
                try:
                    if not os.listdir(full_path):
                        deleted_count += 1
                        os.rmdir(full_path)
                        log_func(f"Folder is empty. Deleting Folder: {item_name}")
                    else:
                        log_func(f"Folder isn't empty. Skipping Folder: {item_name}")
                except OSError as e:
                    log_func(f"Could not delete folder {item_name}: {e}")
            else:
                log_func(f"Skipping folder: {item_name}")

    log_func("...")
    log_func(f"Scan complete! \nTotal items processed: {item_count} \nTotal items moved: {moved_count} \nTotal items deleted: {deleted_count}")

    return moved_history

def undo_last_declutter(folder_path, moved_history, preset_data=None, log_func=print, progress_callback=None):
    if not moved_history:
        log_func("No actions to undo.")
        return

    current_preset = preset_data or DEFAULT_PRESET_DATA
    categories_map = current_preset.get("categories", {})

    log_func("...")
    total = len(moved_history)
    restored_count = 0

    # Restore moved files
    for index, (original_path, current_path) in enumerate(reversed(moved_history), start=1):
        if progress_callback:
            progress_callback(index, total)

        if os.path.exists(current_path):
            try:
                shutil.move(current_path, original_path)
                restored_count += 1
                log_func(f"Restored: {os.path.basename(current_path)}")
            except OSError as e:
                log_func(f"Could not restore {os.path.basename(current_path)}: {e}")
        else:
            log_func(f"File not found (Skipped): {os.path.basename(current_path)}")

    # Clean up empty folders created by the active preset categories + Other
    folders_to_prune = list(categories_map.keys()) + ["Other"]

    for category in folders_to_prune:
        category_dir = os.path.join(folder_path, category)
        if os.path.exists(category_dir) and os.path.isdir(category_dir):
            if not os.listdir(category_dir):
                try:
                    os.rmdir(category_dir)
                    log_func(f"Removed empty category folder: {category}")
                except OSError:
                    pass
            else:
                log_func(f"Skipped category folder because it wasn't empty: {category}")

    log_func("...")
    log_func(f"Undo Complete! Restored {restored_count}/{total} files.")