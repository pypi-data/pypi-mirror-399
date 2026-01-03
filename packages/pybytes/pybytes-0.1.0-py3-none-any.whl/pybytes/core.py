import math

def human_bytes(bytes_size: int, decimal_places: int = 2) -> str:
    """
    Byte'ı insan okuyabilir hale çevirir (maksimum TB).
    Örnek: human_bytes(123456789) → '117.74 MB'
    """
    if bytes_size == 0:
        return "0 B"

    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(bytes_size, 1024)))
    i = min(i, len(size_name) - 1)  # Maksimum TB
    p = math.pow(1024, i)
    s = round(bytes_size / p, decimal_places)
    if i == 4 and bytes_size >= math.pow(1024, 5):
        return f"{s:.2f} TB+"
    return f"{s} {size_name[i]}"

def hb(size: int) -> str:
    """human_bytes kısaltması (1 ondalık basamak)"""
    return human_bytes(size, 1)