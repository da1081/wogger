import tkinter as tk
from tkinter import ttk
import datetime

from src.tooltip import ToolTip
from src.utils import open_folder
from src.time_logger import TimeLogger
from src.manual_entry_window import ManualEntryWindow
from src.app_fonts import FONT_LARGE
from src.week_overview import WeekOverview

class MainUI:
    """
    Builds and manages the main window (treeview, labels, checkboxes, etc.).
    This class does not know how to schedule popups or parse logs;
    it just exposes methods to refresh or reset according to external data.
    """
    def __init__(self, root, time_logger: TimeLogger, on_reset_callback=None, on_settings_callback=None, app_settings=None):
        """
        :param root: A Tk root window (or parent Frame)
        :param time_logger: A TimeLogger instance
        :param on_reset_callback: Called when user clicks the trash button
        :param on_settings_callback: Called when user clicks the settings button
        """
        self.root = root
        self.time_logger = time_logger
        self.on_reset_callback = on_reset_callback
        self.on_settings_callback = on_settings_callback
        self.app_settings = app_settings
        
        self._build_ui()

    def _build_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #
        # Checkbutton to show only today's tasks
        #
        self.show_today_only_var = tk.BooleanVar(value=False)
        show_today_cb = tk.Checkbutton(
            main_frame,
            text="Show Today's Tasks Only",
            variable=self.show_today_only_var,
            command=self.refresh_main_tree
        )
        # Place it at the top/left
        show_today_cb.pack(anchor="w", pady=(0, 5))

        #
        # Top-right frame for trash, open-folder, and settings buttons
        #
        top_right_frame = tk.Frame(main_frame)
        top_right_frame.pack(fill="x", pady=(0, 5))

        # MANUAL INSERT BUTTON
        manual_insert_button = tk.Button(
            top_right_frame,
            text="🖊️",
            command=self.on_click_manual_insert,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        manual_insert_button.pack(side="right", anchor="e")
        ToolTip(manual_insert_button, "Manually insert a task")

        # TRASH BUTTON
        trash_button = tk.Button(
            top_right_frame,
            text="🗑️",
            command=self.on_click_reset,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        trash_button.pack(side="right", anchor="e")
        ToolTip(trash_button, "Click this to reset your time_log.txt")

        #
        # OPEN APPDATA FOLDER BUTTON
        #
        open_folder_button = tk.Button(
            top_right_frame,
            text="📁",
            command=self.on_click_open_data_folder,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        open_folder_button.pack(side="right", anchor="e")
        ToolTip(open_folder_button, "Open the AppData folder")

        # SETTINGS BUTTON
        settings_button = tk.Button(
            top_right_frame,
            text="⚙️",
            command=self.on_click_settings,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        settings_button.pack(side="right", anchor="e")
        ToolTip(settings_button, "Open the advanced settings window")

        # REFRESH BUTTON
        refresh_button = tk.Button(
            top_right_frame,
            text="🔃",
            command=self.on_click_refresh,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        refresh_button.pack(side="right", anchor="e")
        ToolTip(refresh_button, "If you made changes directly to the 'time_log.txt' file, click this to refresh the UI")

        # EXPORT BUTTON
        export_button = tk.Button(
            top_right_frame,
            text="⬇️",
            command=self.on_click_export,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONT_LARGE
        )
        export_button.pack(side="right", anchor="e")
        ToolTip(export_button, "Export work log as CSV")

        #
        # TreeView etc.
        #
        columns = ("task", "file_minutes", "total_pretty")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        self.tree.heading("task", text="Task")
        self.tree.heading("file_minutes", text="Total (min)")
        self.tree.heading("total_pretty", text="Total (pretty)")
        self.tree.column("task", width=200, anchor="w")
        self.tree.column("file_minutes", width=120, anchor="center")
        self.tree.column("total_pretty", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.totals_label = tk.Label(main_frame, text="", font=("TkDefaultFont", 9, "italic"))
        self.totals_label.pack(pady=(5, 0))

        # --- Week Overview Component ---
        self.week_overview = WeekOverview(main_frame, self.time_logger, self.app_settings)
        # self.week_overview.pack(fill="x", pady=(10, 0))
        self.refresh_main_tree()
        self.update_week_overview_visibility()

    def update_week_overview_visibility(self):
        """
        Hide or show the WeekOverview depending on the show_week_overview setting.
        """
        if self.app_settings.show_week_overview:
            self.week_overview.pack(fill="x", pady=(10, 0))
        else:
            self.week_overview.pack_forget()

    def on_click_manual_insert(self):
        """
        Opens a small popup window for the user to manually insert a log line.
        """
        ManualEntryWindow(self.root, self.time_logger, on_save_callback=self._after_manual_entry_save)

    def _after_manual_entry_save(self, success):
        """
        Callback invoked after user tries to save a manual log line.
        If success == True, refresh the tree view.
        """
        if success:
            self.refresh_main_tree()
        else:
            # Optionally show an error dialog or do nothing.
            pass

    def on_click_export(self):
        """
        Exports the time log as CSV and displays a prompt with the output path.
        """
        export_path = self.time_logger.export_time_log_as_csv()
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Export Complete", f"A new export was generated:\n{export_path}")

    def on_click_reset(self):
        if self.on_reset_callback:
            self.on_reset_callback()

    def on_click_settings(self):
        """
        Fire the callback that opens the Settings window.
        """
        if self.on_settings_callback:
            self.on_settings_callback()

    def on_click_open_data_folder(self):
        """
        Opens the current data_folder in the OS file explorer.
        """
        folder = self.app_settings.data_folder
        open_folder(folder)

    def on_click_refresh(self):
        """
        Refresh the treeview with the latest data.
        """
        # Trigger a reload of the log file
        self.time_logger.reload_time_log()
        self.refresh_main_tree()

    def refresh_main_tree(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Check whether "Show Today's Tasks Only" is checked
        if self.show_today_only_var.get():
            tasks_to_display = self.time_logger.get_tasks_for_today()
        else:
            tasks_to_display = self.time_logger.get_all_tasks()

        # Re-populate the tree
        sorted_tasks = sorted(tasks_to_display)
        for task in sorted_tasks:
            file_total = self.time_logger.get_file_total_minutes(task_name=task)
            total_pretty_formatted = self.time_logger.get_pretty_total(task_name=task)
            self.tree.insert(
                "",
                tk.END,
                iid=task,
                values=(task, file_total, total_pretty_formatted)
            )

        # Summaries
        total_in_file = self.time_logger.get_overall_file_minutes()
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        logged_today = self.time_logger.get_logged_minutes_for_date(today_str)

        summary_text = (
            f"Total in time_log.txt: {total_in_file} min | "
            f"Today so far: {logged_today} min"
        )
        self.totals_label.config(text=summary_text)

        self.week_overview.refresh_week_view()