import datetime
import os
import sys
import subprocess

def resource_path(relative_path):
    """
    Get the absolute path to a resource, whether running from source or PyInstaller.
    If running from a PyInstaller 'onefile' build, files are in sys._MEIPASS.
    Otherwise, look inside the 'resources' folder.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, "resources", relative_path)
    else:
        # Running from source; assume resources are in the /resources directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "resources", relative_path)


def compute_minutes_between(hhmm_start, hhmm_end):
    """
    Given two strings in 'HH:MM' format (same day),
    return the integer number of minutes between them.
    """
    fmt = "%H:%M"
    t_start = datetime.datetime.strptime(hhmm_start, fmt)
    t_end = datetime.datetime.strptime(hhmm_end, fmt)
    delta = t_end - t_start
    return int(delta.total_seconds() / 60)


def next_quarter_hour(dt):
    """
    Given a datetime `dt`, return the next time that is exactly
    on a quarter-hour boundary (00, 15, 30, 45) on or after dt.
    If dt is already exactly on a quarter hour (e.g. 12:30:00),
    we return dt unchanged.
    """
    new_dt = dt.replace(second=0, microsecond=0)
    while new_dt.minute % 15 != 0:
        new_dt += datetime.timedelta(minutes=1)
    if new_dt < dt:
        new_dt += datetime.timedelta(minutes=15)
    return new_dt


def format_minutes_pretty(total_minutes, minutes_in_day=1440, days_in_week=7):
    """
    Convert total_minutes into a string like "Xw Yd Zh Zm".

    Parameters:
      - total_minutes (int/float): Total number of minutes.
      - minutes_in_day (int): Number of minutes in one day (default is 1440).
      - days_in_week (int): Number of days in a week (default is 7).

    Returns:
      A string representing the time in weeks, days, hours, and minutes.
      For example, 3500 minutes might be formatted as "2d 10h 20m" 
      depending on the input parameters.
    """
    minutes_per_week = minutes_in_day * days_in_week

    weeks = int(total_minutes // minutes_per_week)
    remainder = total_minutes % minutes_per_week

    days = int(remainder // minutes_in_day)
    remainder = remainder % minutes_in_day

    hours = int(remainder // 60)
    minutes = int(remainder % 60)

    parts = []
    if weeks > 0:
        parts.append(f"{weeks}w")
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    if not parts:
        return "0m"
    return " ".join(parts)


def open_folder(folder):
    """
    Opens the given folder in the system's file explorer.
    If the folder does not exist, it will be created.
    Supports Windows, macOS, and Linux.
    """
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    if sys.platform.startswith('win'):
        os.startfile(folder)
    elif sys.platform.startswith('darwin'):
        subprocess.call(["open", folder])
    else:
        subprocess.call(["xdg-open", folder])