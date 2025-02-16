import json
import os

CONFIG_FILE_NAME: str = "settings.json"

def default_appdata_dir():
    """
    Return a default path for storing user data.
    On Windows, typically %APPDATA%\wogger.
    On other OSes, adapt as needed.
    """
    if os.name == 'nt':  # Windows
        base = os.getenv("APPDATA") or os.path.expanduser("~")
    else:
        # On Linux/Mac, you might prefer ~/.local/share/wogger
        base = os.path.expanduser("~/.local/share")
    return os.path.join(base, "wogger")


class AppSettings:
    """
    Manages application settings, stored in a JSON file.
    """
    def __init__(self):
        self.config_file = os.path.join(default_appdata_dir(), CONFIG_FILE_NAME)
        
        # Default: store data in %APPDATA%\wogger (Windows).
        # Default "work_schedule" in minutes: 8 hours Mon-Fri, 0 on Sat/Sun.
        self._defaults = {
            "sound_on": True,
            "data_folder": default_appdata_dir(),
            "popup_cron": "0,15,30,45 * * * *",  # Every 15 minutes
            "work_schedule": {
                "Monday": 450,
                "Tuesday": 450,
                "Wednesday": 450,
                "Thursday": 450,
                "Friday": 390,
                "Saturday": 0,
                "Sunday": 0
            },
            "standart_work_day": 450,
            "standart_days_in_week": 5,
            "wogger_mode": False,
            "show_week_overview": False
        }

        self._settings_data = {}
        self.load()

    def load(self):
        """
        Loads settings from the config file if it exists; else use defaults.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge loaded data on top of defaults
                    self._settings_data = {**self._defaults, **data}
            except (json.JSONDecodeError, IOError):
                self._settings_data = dict(self._defaults)
        else:
            self._settings_data = dict(self._defaults)

        # Ensure the data folder exists
        self._ensure_data_folder()

    def save(self):
        """
        Persists current settings to disk.
        """
        self._ensure_data_folder()
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._settings_data, f, indent=4)

    def reset_defaults(self):
        """
        Resets in-memory settings to default values, does not auto-save.
        """
        self._settings_data = dict(self._defaults)
        self._ensure_data_folder()

    def _ensure_data_folder(self):
        """
        Creates data_folder if it does not exist.
        """
        folder = self.data_folder
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)

    @property
    def sound_on(self):
        return self._settings_data.get("sound_on", True)

    @sound_on.setter
    def sound_on(self, value: bool):
        self._settings_data["sound_on"] = bool(value)

    @property
    def data_folder(self):
        return self._settings_data.get("data_folder", default_appdata_dir())

    @data_folder.setter
    def data_folder(self, path: str):
        self._settings_data["data_folder"] = path

    @property
    def popup_cron(self):
        return self._settings_data.get("popup_cron", "0,15,30,45 * * * *") # Every 15 minutes
    
    @popup_cron.setter
    def popup_cron(self, cron: str):
        self._settings_data["popup_cron"] = cron

    @property
    def work_schedule(self):
        """
        Returns a dict of { "Monday": minutes, "Tuesday": minutes, ... }
        """
        return self._settings_data.get("work_schedule", {})

    @work_schedule.setter
    def work_schedule(self, schedule_dict):
        self._settings_data["work_schedule"] = schedule_dict

    @property
    def standart_work_day(self):
        return self._settings_data.get("standart_work_day", 450)
    
    @standart_work_day.setter
    def standart_work_day(self, minutes: int):
        self._settings_data["standart_work_day"] = minutes

    @property
    def standart_days_in_week(self):
        return self._settings_data.get("standart_days_in_week", 5)
    
    @standart_days_in_week.setter
    def standart_days_in_week(self, days: int):
        self._settings_data["standart_days_in_week"] = days

    @property
    def wogger_mode(self):
        return self._settings_data.get("wogger_mode", False)
    
    @wogger_mode.setter
    def wogger_mode(self, value: bool):
        self._settings_data["wogger_mode"] = bool(value)

    @property
    def show_week_overview(self):
        return self._settings_data.get("show_week_overview", False)
    
    @show_week_overview.setter
    def show_week_overview(self, value: bool):
        self._settings_data["show_week_overview"] = bool(value)
