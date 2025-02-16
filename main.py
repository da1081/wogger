import tkinter as tk
import datetime
from PIL import Image, ImageTk

from src.time_logger import TimeLogger
from src.main_ui import MainUI
from src.popup_window import PopupWindow
from src.utils import next_quarter_hour, resource_path
from src.settings_manager import AppSettings
from src.settings_window import SettingsWindow
import winsound
from croniter import croniter

"""
The main entry point for the wogger application.
Creates the main window, schedules popups, and wires together the TimeLogger, MainUI, and PopupWindow.

The main window contains a MainUI instance, which displays the current log of work items.
The MainUI instance also contains a "Reset" button, which clears the log.
"""
class WoggerApp:
    """
    The orchestrator: creates the main window, schedules popups,
    and wires together the TimeLogger, MainUI, and PopupWindow.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("wogger (work logger)")
        self.root.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
        self.root.iconbitmap(resource_path("wogger.ico"))

        # Create an AppSettings instance
        self.settings = AppSettings()

        # Create the time-logger
        self.logger = TimeLogger(self.settings)

        # Create the main UI
        self.ui = MainUI(
            root=self.root,
            time_logger=self.logger,
            on_reset_callback=self.on_reset_log,
            on_settings_callback=self.on_settings_click,
            app_settings=self.settings
        )

        # Update the Wogger GIF based on the current setting
        self.update_wogger_gif()

        # Schedule the first popup
        self.schedule_next_popup()

    def update_wogger_gif(self):
        """
        Dynamically updates the Wogger GIF based on the wogger_mode setting.
        If wogger_mode is enabled, it initializes the GIF if not already present.
        If wogger_mode is disabled, it removes the GIF if it exists.
        """
        if self.settings.wogger_mode:
            if not hasattr(self, "wogger_label"):  # Only create if it doesn't exist
                self.setup_wogger_gif(self.root)
        else:
            if hasattr(self, "wogger_label"):  # Remove if it exists
                self.wogger_label.destroy()
                del self.wogger_label  # <-- remove attribute fully
                self.root.update_idletasks()  # Force UI refresh

    def setup_wogger_gif(self, parent):
        """
        Loads 'wogger.gif' and places it at the bottom center of the parent.
        Only initializes if Wogger Mode is enabled.
        """
        if not self.settings.wogger_mode:
            return  # Don't load the GIF if Wogger Mode is off

        # Prevent duplicate labels
        if hasattr(self, "wogger_label"):
            return

        gif_path = resource_path("wogger.gif")
        gif_img = Image.open(gif_path)
        self.wogger_frames = []

        try:
            while True:
                frame = ImageTk.PhotoImage(gif_img.copy())
                self.wogger_frames.append(frame)
                gif_img.seek(gif_img.tell() + 1)
        except EOFError:
            pass  # Reached end of multi-frame GIF

        self.wogger_label = tk.Label(parent, image=self.wogger_frames[0])
        self.wogger_label.pack(side="bottom")

        def on_wogger_click(event):
            if self.settings.sound_on:
                wav_path = resource_path("wogger.wav")
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            def show_frame(idx=0):
                if idx < len(self.wogger_frames):
                    self.wogger_label.config(image=self.wogger_frames[idx])
                    self.root.after(100, show_frame, idx + 1)
                else:
                    self.wogger_label.config(image=self.wogger_frames[0])

            show_frame()

        self.wogger_label.bind("<Button-1>", on_wogger_click)

    def on_reset_log(self):
        """
        When the trash button is clicked, reset the log in the logger
        and refresh the UI.
        """
        self.logger.reset_time_log()
        self.ui.refresh_main_tree()
    
    def on_settings_click(self):
        """
        Opens the settings window.
        """
        SettingsWindow(self, self.settings, self.ui)

    def schedule_next_popup(self):
        """
        Schedules the next popup based on the cron expression in settings.popup_cron.
        """
        now = datetime.datetime.now()
        cron_expr = self.settings.popup_cron  # e.g., "0,15,30,45 * * * *"
        cron_iter = croniter(cron_expr, now)
        next_popup_time = cron_iter.get_next(datetime.datetime)
        delta_ms = int((next_popup_time - now).total_seconds() * 1000)
        self.root.after(delta_ms, lambda: self.show_popup_and_reschedule(next_popup_time))

    def show_popup_and_reschedule(self, interval_end):
        """
        Shows a popup for the interval from the previous scheduled time up to interval_end,
        then schedules the next popup.
        """
        # Schedule the next popup immediately (so it's always queued)
        self.schedule_next_popup()

        # Compute the previous scheduled time using croniter.
        cron_expr = self.settings.popup_cron
        cron_iter = croniter(cron_expr, interval_end)
        interval_start = cron_iter.get_prev(datetime.datetime)

        PopupWindow(
            parent=self.root,
            interval_start=interval_start,
            interval_end=interval_end,
            known_tasks=self.logger.get_all_tasks(),
            on_submit=self._on_popup_submit
        )

    def _on_popup_submit(self, task_name, interval_start, interval_end):
        """
        Handler when user clicks "Submit" in the popup.
        """
        self.logger.log_work_item(task_name, interval_start, interval_end)
        self.ui.refresh_main_tree()

    def on_main_window_close(self):
        """
        Closes the main window and stops the entire application (including popups).
        """
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WoggerApp()
    app.run()
