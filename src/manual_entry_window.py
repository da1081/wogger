import tkinter as tk
import datetime

class ManualEntryWindow:
    """
    A small window for manually inserting a single line of text in the format:
       YYYY-MM-DD HH:MM - HH:MM | Task Name
    The Submit button stays disabled until the input is valid.
    """
    def __init__(self, parent, time_logger, on_save_callback):
        """
        :param parent: The parent (a Tk or Toplevel)
        :param time_logger: An instance of TimeLogger
        :param on_save_callback: A function that receives True/False indicating success/fail
        """
        self.parent = parent
        self.time_logger = time_logger
        self.on_save_callback = on_save_callback

        # Create a Toplevel for this manual entry
        self.top = tk.Toplevel(self.parent)
        self.top.title("Manually Insert a Task")
        self.top.resizable(False, False)
        # self.top.grab_set()  # optional: make it modal
        self.line_var = tk.StringVar(value=self._generate_default_entry())
        
        self._build_ui()
        self._setup_validation()

    def _build_ui(self):
        # A label describing the format
        tk.Label(
            self.top,
            text="Enter one line in the format:\nYYYY-MM-DD HH:MM - HH:MM | Some Task",
            justify="left"
        ).pack(padx=10, pady=(10, 5))

        # The entry field
        entry_frame = tk.Frame(self.top)
        entry_frame.pack(padx=10, pady=(0, 5))
        
        self.entry = tk.Entry(entry_frame, textvariable=self.line_var, width=50)
        self.entry.pack(side="left")
        self.entry.focus_set()

        # Submit & Cancel buttons at the bottom
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(padx=10, pady=10, fill="x", expand=True)

        self.submit_btn = tk.Button(btn_frame, text="Submit", command=self.on_submit, state=tk.DISABLED)
        self.submit_btn.pack(side="left")

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side="left", padx=(10, 0))

    def _setup_validation(self):
        """
        Set up a trace on self.line_var. Whenever the user types, we re-check validity.
        """
        self.line_var.trace_add("write", self._on_input_changed)

    def _on_input_changed(self, *args):
        """
        Called whenever the entry changes. We check if it's valid.
        """
        line_text = self.line_var.get().strip()
        if self.time_logger.is_valid_manual_log_line(line_text):
            self.submit_btn.config(state=tk.NORMAL)
        else:
            self.submit_btn.config(state=tk.DISABLED)

    def on_submit(self):
        """
        If valid, append to time_log.txt via time_logger and close.
        """
        line_text = self.line_var.get().strip()
        success = self.time_logger.append_manual_log_line(line_text)
        self.on_save_callback(success)
        self.top.destroy()

    def on_cancel(self):
        """
        Close without saving.
        """
        self.on_save_callback(False)
        self.top.destroy()

    def _generate_default_entry(self):
        """
        Generates a placeholder entry in the format:
        YYYY-MM-DD HH:** - **:** | ****
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")  # Get current hour

        return f"{date_str} {hour_str}:** - **:** | ****"
