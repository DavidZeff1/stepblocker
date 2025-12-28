from datetime import datetime, timezone
from .config import SECRET

def validate_code(code):
    """Check if the unlock code is valid for current or previous hour."""
    now = datetime.now(timezone.utc)
    hour_block = int(now.timestamp() / 3600)
    date_str = now.strftime("%Y-%m-%d")
    
    for offset in range(2):
        check_hour = hour_block - offset
        input_str = f"{SECRET}-{date_str}-{check_hour}"
        hash_val = 0
        for char in input_str:
            hash_val = ((hash_val << 5) - hash_val) + ord(char)
            hash_val = hash_val & 0xFFFFFFFF
            if hash_val >= 0x80000000:
                hash_val -= 0x100000000
        if code == f"{abs(hash_val) % 1000000:06d}":
            return True
    return False
