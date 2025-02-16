import tkinter as tk
from tkinter import ttk
import winsound
from src.settings_manager import AppSettings
from src.utils import resource_path

class PopupWindow:
    """
    Represents the 15-minute "What did you work on?" popup.
    """
    def __init__(self, parent, interval_start, interval_end, known_tasks, on_submit, sound_on=True):
        """
        :param parent: The parent window (or root)
        :param interval_start: datetime for the start of the interval
        :param interval_end: datetime for the end of the interval
        :param known_tasks: List or set of existing tasks (for combobox)
        :param on_submit: Callback when the user clicks submit, signature: f(task_name, start_dt, end_dt)
        :param sound_on: Whether to play a sound on popup
        """
        self.parent = parent
        self.interval_start = interval_start
        self.interval_end = interval_end
        self.known_tasks = sorted(known_tasks)
        self.on_submit = on_submit
        self.sound_on = sound_on

        # Create the top-level popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Time Tracking")
        self.popup.attributes("-topmost", True)
        
        # Play wogger.wav sound if sound is enabled.
        if self.sound_on:
            wav_path = resource_path("wogger.wav")
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        self._build_ui()

    def _build_ui(self):
        # Show the interval label
        interval_label = f"{self.interval_start.strftime('%H:%M')} - {self.interval_end.strftime('%H:%M')}"
        tk.Label(
            self.popup,
            text=f"What did you work on during {interval_label}?",
            font=("TkDefaultFont", 10, "bold")
        ).pack(padx=10, pady=10)

        frame = tk.Frame(self.popup)
        frame.pack(padx=10, pady=5)

        # A combobox for selecting existing tasks
        tk.Label(frame, text="Select a previous task:").grid(row=0, column=0, sticky="w")
        self.combo_var = tk.StringVar()
        combo = ttk.Combobox(
            frame,
            textvariable=self.combo_var,
            values=self.known_tasks,
            state="readonly"
        )
        combo.grid(row=0, column=1, padx=5, pady=5)

        # An entry for new tasks
        tk.Label(frame, text="Or type a new task:").grid(row=1, column=0, sticky="w")
        self.new_task_var = tk.StringVar()
        new_task_entry = tk.Entry(frame, textvariable=self.new_task_var, width=30)
        new_task_entry.grid(row=1, column=1, padx=5, pady=5)
        new_task_entry.focus()  # Focus on the new-task entry by default

        submit_btn = tk.Button(self.popup, text="Submit", command=self._on_submit)
        submit_btn.pack(pady=5)

    def _on_submit(self):
        selected = self.combo_var.get().strip()
        typed = self.new_task_var.get().strip()

        if typed:
            task_name = typed
        elif selected:
            task_name = selected
        else:
            task_name = "Unspecified"

        # Callback to the outside world
        self.on_submit(task_name, self.interval_start, self.interval_end)
        self.popup.destroy()
