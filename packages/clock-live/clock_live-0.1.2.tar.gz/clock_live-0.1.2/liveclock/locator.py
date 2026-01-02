import requests

def get_local_tz():
    """Detects the user's timezone based on IP address."""
    try:
        response = requests.get("https://ipapi.co/timezone/", timeout=5)
        if response.status_status == 200:
            return response.text.strip()
    except Exception:
        pass
    return "UTC"  # Fallback
