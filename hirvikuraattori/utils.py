def humanize_file_size(num_bytes, suffix="B"):
    # Source: https://stackoverflow.com/a/1094933
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f}{unit}{suffix}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}Yi{suffix}"
