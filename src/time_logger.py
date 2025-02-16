import os
import datetime
from src.settings_manager import AppSettings
from src.utils import compute_minutes_between, format_minutes_pretty

class TimeLogger:
    """
    Handles reading/writing the time_log.txt file and tracking minutes per task.
    """

    def __init__(self, app_settings: AppSettings):
        """
        :param app_settings: An instance of AppSettings
        """
        self.app_settings = app_settings
        self.log_task_minutes = {}     # { task_name: total_minutes_in_file }

        self._parse_time_log_file()

    def _get_log_path(self):
        """
        Returns the full path to time_log.txt based on current app_settings.
        """
        return os.path.join(self.app_settings.data_folder, "time_log.txt")

    def _parse_time_log_file(self):
        """
        Reads time_log.txt if it exists.
        """
        log_path = self._get_log_path()
        if not os.path.isfile(log_path):
            return

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "|" not in line:
                    continue
                time_part, task_part = line.split("|", 1)
                task_name = task_part.strip()

                # Example line: "2025-02-05 12:00 - 12:15 | Some Task"
                parts = time_part.split()
                if len(parts) < 4:
                    continue
                hhmm_start = parts[1]
                hhmm_end = parts[3]

                try:
                    minutes_diff = compute_minutes_between(hhmm_start, hhmm_end)
                except:
                    continue

                self.log_task_minutes[task_name] = self.log_task_minutes.get(task_name, 0) + minutes_diff

    def reload_time_log(self):
        """
        Reloads the time_log.txt file and re-parses it.
        """
        self.log_task_minutes.clear()
        self._parse_time_log_file()

    def get_logged_minutes_for_date(self, date_str: str) -> int:
        """
        Returns the total minutes logged on a specific date (YYYY-MM-DD)
        by scanning time_log.txt line by line.
        """
        log_path = self._get_log_path()
        if not os.path.isfile(log_path):
            return 0

        total_for_day = 0
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line:
                    continue

                time_part, _task_part = line.split("|", 1)
                parts = time_part.split()
                if len(parts) < 4:
                    continue

                # parts[0] is the date like "2025-03-02"
                line_date = parts[0]
                if line_date == date_str:
                    hhmm_start = parts[1]
                    hhmm_end = parts[3]
                    try:
                        minutes_diff = compute_minutes_between(hhmm_start, hhmm_end)
                        total_for_day += minutes_diff
                    except:
                        pass
        return total_for_day

    def get_tasks_for_today(self):
        """
        Returns a set of task names that were logged today (according to time_log.txt).
        """
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_path = self._get_log_path()
        tasks_today = set()

        if not os.path.isfile(log_path):
            return tasks_today

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line:
                    continue
                
                time_part, task_part = line.split("|", 1)
                parts = time_part.split()
                if len(parts) < 4:
                    continue

                line_date = parts[0]  # e.g. "2025-05-20"
                if line_date == today_str:
                    task_name = task_part.strip()
                    tasks_today.add(task_name)
        
        return tasks_today

    def log_work_item(self, task_name, start_dt, end_dt):
        """
        Appends a line to time_log.txt and updates in-memory totals.
        """
        log_path = self._get_log_path()
        os.makedirs(self.app_settings.data_folder, exist_ok=True)

        date_str = start_dt.strftime("%Y-%m-%d")
        start_str = start_dt.strftime("%H:%M")
        end_str = end_dt.strftime("%H:%M")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{date_str} {start_str} - {end_str} | {task_name}\n")

        diff_minutes = compute_minutes_between(start_str, end_str)
        self.log_task_minutes[task_name] = self.log_task_minutes.get(task_name, 0) + diff_minutes

    def reset_time_log(self):
        """
        Moves time_log.txt to a backup, clears in-memory data.
        """
        log_path = self._get_log_path()
        if os.path.exists(log_path):
            now_str = datetime.datetime.now().strftime("%Y%m%d%H%M")
            backup_name = f"time_log.txt.bak{now_str}"
            backup_path = os.path.join(self.app_settings.data_folder, backup_name)
            os.rename(log_path, backup_path)

        self.log_task_minutes.clear()

    def get_all_tasks(self):
        return self.log_task_minutes.keys()

    def get_file_total_minutes(self, task_name):
        return self.log_task_minutes.get(task_name, 0)

    def get_overall_file_minutes(self):
        return sum(self.log_task_minutes.values())
    
    def is_valid_manual_log_line(self, line_str: str) -> bool:
        """
        Returns True if line_str can be parsed as:
           YYYY-MM-DD HH:MM - HH:MM | Some Task
        Otherwise False.
        """
        line_str = line_str.strip()
        if "|" not in line_str:
            return False
        time_part, task_part = line_str.split("|", 1)
        task_part = task_part.strip()
        if not task_part:
            return False

        parts = time_part.split()
        if len(parts) < 4:
            return False
        date_str = parts[0]
        hhmm_start = parts[1]
        dash = parts[2]
        hhmm_end = parts[3]
        if dash != "-":
            return False

        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # We intentionally do not check negative difference here so that the format is accepted.
            compute_minutes_between(hhmm_start, hhmm_end)
        except Exception:
            return False

        return True

    def append_manual_log_line(self, line_str: str) -> bool:
        """
        If valid, parse the line, and if the resulting time interval is not negative,
        append the line to time_log.txt and update in-memory totals.
        If the time interval is negative, show an error popup and return False.
        """
        if not self.is_valid_manual_log_line(line_str):
            return False

        line_str = line_str.strip()
        time_part, task_part = line_str.split("|", 1)
        task_part = task_part.strip()

        parts = time_part.split()
        date_str = parts[0]
        hhmm_start = parts[1]
        hhmm_end = parts[3]

        minutes_diff = compute_minutes_between(hhmm_start, hhmm_end)
        if minutes_diff < 0:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "⏳ Invalid Time Interval",
                ("⚠️ The time interval results in a negative duration.\n\n"
                "🕒 Please ensure that the end time is later than the start time.\n\n"
                "If you need to manually adjust past entries, you can edit the log file directly 👇\n\n"
                "👉 Open AppData folder 📂 to modify `time_log.txt` as needed.\n"
                "👉 Then press refresh button 🔃 to refresh wogger!"
                ),
                icon="warning", 
            )
            return False


        # Write the valid line to the log file.
        log_path = self._get_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line_str + "\n")

        # Update in-memory totals.
        self.log_task_minutes[task_part] = self.log_task_minutes.get(task_part, 0) + minutes_diff

        return True

    def get_pretty_total(self, task_name: str = None) -> str:
        """
        Returns a pretty-formatted string (like "1d 2h 15m") representing the total logged time.
        If task_name is provided, only entries matching that task are included; otherwise, all entries are summed.
        Uses raw logged minutes and formats them using the configured standard work day.
        """
        total_minutes = 0
        log_path = self._get_log_path()
        if not os.path.isfile(log_path):
            return "0m"

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line:
                    continue

                time_part, task_part = line.split("|", 1)
                task_line = task_part.strip()
                if task_name is not None and task_line.lower() != task_name.lower():
                    continue

                parts = time_part.split()
                if len(parts) < 4:
                    continue
                # parts[1] is the start time and parts[3] is the end time in "HH:MM" format
                hhmm_start = parts[1]
                hhmm_end = parts[3]
                try:
                    entry_minutes = compute_minutes_between(hhmm_start, hhmm_end)
                except Exception:
                    continue
                total_minutes += entry_minutes

        pretty_str = format_minutes_pretty(
            total_minutes,
            minutes_in_day=self.app_settings.standart_work_day,
            days_in_week=self.app_settings.standart_days_in_week
        )
        return pretty_str

    def get_time_log_entries(self) -> list:
        """
        Reads time_log.txt and returns a list of dictionaries, where each dictionary
        represents one log entry with the following keys:
        - date (str, "YYYY-MM-DD")
        - day (str, e.g., "Monday")
        - start_time (str, "HH:MM")
        - end_time (str, "HH:MM")
        - duration (int, duration in minutes)
        - task (str)
        """
        entries = []
        log_path = self._get_log_path()
        if not os.path.isfile(log_path):
            return entries

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line:
                    continue
                try:
                    time_part, task_part = line.split("|", 1)
                except Exception:
                    continue
                task = task_part.strip()
                parts = time_part.split()
                if len(parts) < 4:
                    continue
                date_str = parts[0]
                start_time = parts[1]
                dash = parts[2]
                end_time = parts[3]
                if dash != "-":
                    continue
                try:
                    duration = compute_minutes_between(start_time, end_time)
                except Exception:
                    duration = None
                try:
                    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    day_of_week = dt.strftime("%A")
                except Exception:
                    day_of_week = ""
                entry = {
                    "date": date_str,
                    "day": day_of_week,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "task": task
                }
                entries.append(entry)
        return entries
    
    # def get_time_log_as_json(self) -> str:
    #     """
    #     Returns the content of time_log.txt as a JSON string.
    #     The JSON is a list of entries, where each entry is a dictionary with keys:
    #       "date", "day", "start_time", "end_time", "duration", "task".
    #     """
    #     import json
    #     entries = self.get_time_log_entries()
    #     return json.dumps(entries, indent=2)

    def export_time_log_as_csv(self) -> str:
        """
        Exports the content of time_log.txt as a CSV file formatted for data analysis.
        The CSV file will include the following columns:
          - Date (YYYY-MM-DD)
          - Day (e.g., Monday)
          - Start Time (HH:MM)
          - End Time (HH:MM)
          - Duration (min)
          - Task

        The exported file is named "time_log_export_YYYYMMDDhhmmss.csv" and is saved in the
        appdata folder (self.app_settings.data_folder). Any existing file with the same name is overwritten.

        Returns:
            The full path to the exported CSV file.
        """
        import csv
        now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        export_filename = f"time_log_export_{now_str}.csv"
        export_path = os.path.join(self.app_settings.data_folder, export_filename)
        
        entries = self.get_time_log_entries()
        with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Day", "Start Time", "End Time", "Duration (min)", "Task"])
            for entry in entries:
                writer.writerow([
                    entry["date"],
                    entry["day"],
                    entry["start_time"],
                    entry["end_time"],
                    entry["duration"],
                    entry["task"]
                ])
        return export_path


