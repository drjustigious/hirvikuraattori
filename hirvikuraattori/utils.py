from typing import Dict


IMEI = "imei"
DATE = "date"
SIGNAL = "signal"
BATTERY = "battery"
TEMPERATURE = "temperature"
PHOTOS = "photos"
TOTAL_MEMORY = "total_memory"
FREE_MEMORY = "free_memory"


def humanize_file_size(num_bytes, suffix="B"):
    # Source: https://stackoverflow.com/a/1094933
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f}{unit}{suffix}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}Yi{suffix}"


def extract_camera_metadata(message: str) -> Dict:
    """Try to extract camera metadata from the email message.
    This script assumes the metadata is in the Burrel format:

        Date:01-01-2021
        Signal:Very Good(4G)
        Battery:Full
        Temperature:6 degree Celsius(C)
        Total photos:12, Total videos:0
        Total space:30516M, Free space:30478M
        IMEI/MEID:869492xxxyyyzzz

    """
    if "IMEI/MEID" not in message:
        return None

    rows = message.split("\r\n")
    fields = []
    for row in rows:
        fields.extend(row.split(","))
    fields = [field.strip() for field in fields]
    raw_data = {}

    for field in fields:
        key = field.split(":")[0]
        value = field[len(key)+1:]
        raw_data[key] = value

    metadata = {
        IMEI: raw_data.get("IMEI/MEID", ""),
        DATE: raw_data.get("Date", ""),
        SIGNAL: raw_data.get("Signal", ""),
        BATTERY: raw_data.get("Battery", ""),
        TEMPERATURE: raw_data.get("Temperature", "").split(" ")[0],
        PHOTOS: raw_data.get("Total photos", ""),
        TOTAL_MEMORY: raw_data.get("Total space", ""),
        FREE_MEMORY: raw_data.get("Free space", ""),
    }
    print(metadata)  # Debug. TODO: Remove.
    return metadata
