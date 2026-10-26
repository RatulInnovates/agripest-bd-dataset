import os
import csv
from PIL import Image, ExifTags

# Configuration
RAW_DATA_DIR = "data/raw/T3-Grasshopper"
CSV_FILE = "data/master_inventory.csv"

# The 15 metadata fields
HEADERS = [
    "image_id", "original_filename", "split_assignment", "species_class", 
    "host_crop", "life_stage", "capture_environment", "background_surface", 
    "lighting_condition", "location", "capture_date_time", "device_model", 
    "image_width", "image_height", "textual_caption"
]

def get_exif_data(img):
    """Extracts DateTime and Device Model from EXIF if available."""
    exif_data = {"date_time": "Unknown", "model": "Unknown"}
    try:
        exif = img._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal' or tag == 'DateTime':
                    exif_data["date_time"] = str(value)
                elif tag == 'Model':
                    exif_data["model"] = str(value).strip()
    except Exception:
        pass
    return exif_data

def main():
    # Initialize CSV if it doesn't exist
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()

        # Dictionary to store the previous answers for fast batch entry
        last_entry = {
            "host_crop": "", "life_stage": "", "capture_environment": "",
            "background_surface": "", "lighting_condition": "", "location": ""
        }
        
        image_counter = 1

        print("--- AgriPest-BD Metadata Logger ---")
        print("Leave blank and press Enter to copy the previous value.\n")

        for filename in os.listdir(RAW_DATA_DIR):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            filepath = os.path.join(RAW_DATA_DIR, filename)
            
            with Image.open(filepath) as img:
                img.show() # Opens the image so you can see what you are tagging
                
                width, height = img.size
                exif = get_exif_data(img)

                print(f"\nProcessing: {filename}")
                
                # Prompt for manual fields
                for field in last_entry.keys():
                    default = last_entry[field]
                    prompt = f"{field} [{default}]: " if default else f"{field}: "
                    user_input = input(prompt).strip()
                    
                    if user_input:
                        last_entry[field] = user_input

                caption = input("textual_caption (or leave blank): ").strip()

                # Build the row
                row = {
                    "image_id": f"AGRI_{image_counter:05d}",
                    "original_filename": filename,
                    "split_assignment": "Pending", # Assigned later via Roboflow
                    "species_class": "Pending",    # Assigned later via Roboflow
                    "host_crop": last_entry["host_crop"],
                    "life_stage": last_entry["life_stage"],
                    "capture_environment": last_entry["capture_environment"],
                    "background_surface": last_entry["background_surface"],
                    "lighting_condition": last_entry["lighting_condition"],
                    "location": last_entry["location"],
                    "capture_date_time": exif["date_time"],
                    "device_model": exif["model"],
                    "image_width": width,
                    "image_height": height,
                    "textual_caption": caption
                }

                writer.writerow(row)
                print(f"-> Saved AGRI_{image_counter:05d} to database.")
                image_counter += 1

if __name__ == "__main__":
    main()