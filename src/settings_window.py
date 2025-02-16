import tkinter as tk
from tkinter import ttk, messagebox
from src.app_fonts import FONT
import winsound
from src.main_ui import MainUI
from src.settings_manager import AppSettings
from src.utils import resource_path

class SettingsWindow:
    """
    A simple Toplevel window where the user can edit advanced settings,
    including a custom weekly schedule (minutes per day).
    """
    def __init__(self, app, app_settings: AppSettings, main_ui: MainUI):
        """
        :param app: The WoggerApp instance
        :param app_settings: An AppSettings instance
        """
        self.app = app  # Store the WoggerApp here
        self.app_settings = app_settings
        self.main_ui = main_ui

        # Create the Toplevel using app.root
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Advanced Settings")
        self.window.resizable(False, False)

        # self.window.grab_set()  # optional: block main window while this is open (modal)

        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.schedule_vars = {}  # day -> StringVar

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack()

        # --- Sound on/off ---
        self.sound_var = tk.BooleanVar(value=self.app_settings.sound_on)
        tk.Checkbutton(
            frame,
            text="🔊 Turn the sound on/off",
            variable=self.sound_var, font=FONT
        ).grid(row=0, column=0, columnspan=2, sticky="e", pady=5)

        # --- Data Folder ---
        tk.Label(frame, text="📁 Data Folder:", font=FONT).grid(row=1, column=0, sticky="e", padx=(0,5))
        self.data_folder_var = tk.StringVar(value=self.app_settings.data_folder)
        tk.Entry(frame, textvariable=self.data_folder_var, width=40).grid(row=1, column=1, pady=5)

        # --- Popup Interval ---
        tk.Label(frame, text="⌛ Popup Schedule (cron expression):", font=FONT).grid(row=2, column=0, sticky="e", padx=(0,5))
        self.popup_cron_var = tk.StringVar(value=str(self.app_settings.popup_cron))
        tk.Entry(frame, textvariable=self.popup_cron_var, width=40).grid(row=2, column=1, pady=5, sticky="w")

        # --- Work Schedule (minutes per day) ---
        schedule_frame = tk.LabelFrame(frame, text="Minutes to Work Each Day 📆", font=FONT)
        schedule_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10,5))

        for i, day in enumerate(self.days_of_week):
            tk.Label(schedule_frame, text=f"{day}:", font=FONT).grid(row=i, column=0, sticky="e", padx=(5,5), pady=2)
            self.schedule_vars[day] = tk.StringVar(value=str(self.app_settings.work_schedule.get(day, 0)))
            tk.Entry(schedule_frame, textvariable=self.schedule_vars[day], width=6).grid(row=i, column=1, sticky="w")

        # --- Separator ---
        ttk.Separator(frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        tk.Label(schedule_frame, text="Standarts used for day & week formating:", font=FONT).grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        # --- Standard Work Day ---
        tk.Label(schedule_frame, text="Standard Work Day:", font=FONT).grid(row=7, column=0, sticky="e", padx=(5,5), pady=2)
        self.schedule_vars["Standard Work Day"] = tk.StringVar(value=str(self.app_settings.standart_work_day))
        tk.Entry(schedule_frame, textvariable=self.schedule_vars["Standard Work Day"], width=6).grid(row=7, column=1, sticky="w")

        # --- Standard Days in Week ---
        tk.Label(schedule_frame, text="Standard Days in Week:", font=FONT).grid(row=8, column=0, sticky="e", padx=(5,5), pady=2)
        self.schedule_vars["Standard Days in Week"] = tk.StringVar(value=str(self.app_settings.standart_days_in_week))
        tk.Entry(schedule_frame, textvariable=self.schedule_vars["Standard Days in Week"], width=6).grid(row=8, column=1, sticky="w")

        # --- Buttons ---
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=999, column=0, columnspan=2, pady=10, sticky="ew")

        reset_btn = tk.Button(btn_frame, text="Reset to Defaults", command=self.on_reset_click, font=FONT)
        reset_btn.pack(side="left", padx=(0,10))

        save_btn = tk.Button(btn_frame, text="Save", command=self.on_save_click, font=FONT)
        save_btn.pack(side="left")

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.on_cancel_click, font=FONT)
        cancel_btn.pack(side="left", padx=(10,0))

        # 🐸 Wogger Mode Button
        wogger_btn = tk.Button(
            btn_frame,
            text="🐸",
            command=self.on_wogger_mode_toggle,
            font=FONT,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2"
        )
        wogger_btn.pack(side="right")

        # 📅 Show Week Overview Button
        show_week_btn = tk.Button(
            btn_frame,
            text="📅",
            command=self.on_show_week_overview_toggle,
            font=FONT,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
        )
        show_week_btn.pack(side="right")

    def on_wogger_mode_toggle(self):
        self.app_settings.wogger_mode = not self.app_settings.wogger_mode
        self.app_settings.save()

        # If sound is on, play the wogger.wav
        if self.app_settings.sound_on:
            wav_path = resource_path("wogger.wav")
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        # Now we can directly call WoggerApp.update_wogger_gif()
        self.app.update_wogger_gif()

    def on_show_week_overview_toggle(self):
        self.app_settings.show_week_overview = not self.app_settings.show_week_overview
        self.app_settings.save()

        # Immediately reflect this change in the main UI:
        self.main_ui.update_week_overview_visibility()

    def on_reset_click(self):
        """
        Reset all settings in memory to defaults and update the UI.
        """
        self.app_settings.reset_defaults()
        self.sound_var.set(self.app_settings.sound_on)
        self.data_folder_var.set(self.app_settings.data_folder)
        for day in self.days_of_week:
            self.schedule_vars[day].set(str(self.app_settings.work_schedule.get(day, 0)))

    def on_save_click(self):
        """
        Update app_settings from the UI, then save to disk.
        """
        # Update basic settings
        self.app_settings.sound_on = self.sound_var.get()
        self.app_settings.data_folder = self.data_folder_var.get()

        # Retrieve and validate the cron expression from the UI.
        cron_expr = str(self.popup_cron_var.get()).strip()
        if not self._is_valid_cron(cron_expr):
            tk.messagebox.showerror(
                "Invalid Cron Expression",
                (
                    "The cron expression is invalid. A valid cron expression should have 5 fields separated by spaces.\n"
                    "Example: '0,15,30,45 * * * *' for every 15 minutes.\n"
                    "Please refer to online documentation for more details."
                )
            )
            return
        # Only update the setting if the expression is valid.
        self.app_settings.popup_cron = cron_expr

        # Build a new work schedule dict from the UI values.
        new_schedule = {}
        for day in self.days_of_week:
            val_str = self.schedule_vars[day].get().strip()
            try:
                new_schedule[day] = int(val_str)
            except ValueError:
                # Fallback to 0 if conversion fails.
                new_schedule[day] = 0
        self.app_settings.work_schedule = new_schedule

        # Save the updated settings and close the settings window.
        self.app_settings.save()
        self.window.destroy()

    def on_cancel_click(self):
        """
        Close without saving changes.
        """
        self.window.destroy()

    def _is_valid_cron(self, cron_expr):
        """
        Validate a cron expression. A valid cron expression has 5 fields separated by spaces.
        This function now accepts fields that contain only the allowed characters.
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            return False
        for part in parts:
            cleaned = part.replace('*', '').replace(',', '').replace('-', '')
            # If 'cleaned' is empty, it means the part contained only allowed characters.
            if cleaned and not cleaned.isdigit():
                return False
        return True
