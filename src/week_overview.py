import tkinter as tk
import datetime
import random
from src.app_fonts import FONT_SMALL, FONT, FONT_LARGE, FONT_BOLD

class WeekOverview(tk.Frame):
    """
    Displays an overview for the current week showing, for each day:
      - The day name and date
      - Expected minutes / Logged minutes
      - A random emoji from day-specific or ratio-based pools
      - A small progress bar to indicate ratio of logged vs. expected
      - The difference from the goal in minutes (colored accordingly)
    Provides navigation to previous/next week.
    """

    def __init__(self, parent, time_logger, app_settings, **kwargs):
        super().__init__(parent, **kwargs)
        self.time_logger = time_logger
        self.app_settings = app_settings
        self.current_week_start = self.get_week_start(datetime.datetime.now())
        self.create_widgets()
        self.render_week()

    def get_week_start(self, date):
        """Return the Monday for the week containing 'date'."""
        return date - datetime.timedelta(days=date.weekday())

    def create_widgets(self):
        # Navigation frame with previous/next buttons and week label
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill="x", pady=5)

        self.prev_button = tk.Button(
            nav_frame,
            text="← Previous Week",
            command=self.prev_week,
            font=FONT
        )
        self.prev_button.pack(side="left")

        self.week_label = tk.Label(nav_frame, text="", font=FONT_BOLD)
        self.week_label.pack(side="left", expand=True)

        self.next_button = tk.Button(
            nav_frame,
            text="Next Week →",
            command=self.next_week,
            font=FONT
        )
        self.next_button.pack(side="right")
        
        # Frame for the daily overview grid
        self.days_frame = tk.Frame(self)
        self.days_frame.pack(fill="x", pady=5)

    def render_week(self):
        # Clear previous widgets in days_frame
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # Update week label
        week_end = self.current_week_start + datetime.timedelta(days=6)
        self.week_label.config(
            text=f"{self.current_week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
        )

        # Define the days in order
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today_date = datetime.datetime.now().date()

        for i, day in enumerate(days):
            # Compute the date for this day
            day_date = self.current_week_start + datetime.timedelta(days=i)
            date_str = day_date.strftime("%Y-%m-%d")

            # Expected minutes from the app settings
            expected = self.app_settings.work_schedule.get(day, 0)
            # Logged minutes for this day
            logged = self.time_logger.get_logged_minutes_for_date(date_str)
            
            # Build a small frame for this day
            day_frame = tk.Frame(self.days_frame, borderwidth=1, relief="solid", padx=2, pady=2)
            
            # Highlight today's cell
            if day_date.date() == today_date:
                day_frame.config(bg="lightyellow")

            day_frame.grid(row=0, column=i, padx=2, sticky="nsew")

            # Day label
            tk.Label(
                day_frame,
                text=day,
                font=FONT_BOLD,
                bg=day_frame.cget("bg")
            ).pack()

            # Date label
            tk.Label(
                day_frame,
                text=date_str,
                font=FONT_SMALL,
                bg=day_frame.cget("bg")
            ).pack()

            # Expected vs. Logged
            tk.Label(
                day_frame,
                text=f"Expected: {expected} min",
                font=FONT_SMALL,
                bg=day_frame.cget("bg")
            ).pack()
            tk.Label(
                day_frame,
                text=f"Logged: {logged} min",
                font=FONT_SMALL,
                bg=day_frame.cget("bg")
            ).pack()

            # Choose a random emoji for that day based on ratio
            ratio = (logged / expected) if expected else 0
            emoji = self.choose_emoji(day, ratio)

            tk.Label(
                day_frame,
                text=emoji,
                font=FONT_LARGE,
                bg=day_frame.cget("bg")
            ).pack()

            # Draw a progress bar
            self.draw_progress_bar(day_frame, ratio, expected, logged)

    def choose_emoji(self, day_name, ratio):
        """
        Returns a randomly selected emoji based on day-specific pools for weekends
        (Saturday/Sunday) or ratio-based pools for workdays.
        
        For workdays:
        - If ratio >= 1.0, a pool of celebratory/happy emojis is used.
        - If ratio >= 0.75, a pool of upbeat emojis is used.
        - If ratio >= 0.5, a pool of neutral/hesitant emojis is used.
        - Otherwise, a pool of sad/struggling emojis is used.
        """
        day_lower = day_name.lower()
        
        # For weekends, use day-specific pools.
        if day_lower in ["saturday", "sunday"]:
            weekend_pools = {
                "saturday": ["🎉", "🥳", "🍻", "🕺", "🍹", "🎊", "🤩", "🎈", "🥂", "🍾", "😎"],
                "sunday":   ["😴", "💤", "🌙", "🛌", "😌", "😇", "☕", "📖", "🍳", "🥐", "😴"]
            }
            return random.choice(weekend_pools[day_lower])
        
        # For workdays (Monday-Friday), use ratio-based pools.
        if ratio >= 1.0:
            exceeded_pool = [
                "🔥", "😎", "🚀", "💥", "🏆", "🥇", "✨", "💫",
                "😃", "😁", "🎯", "🏅", "🌟", "🤩", "🥳", "🎊",
                "🎉", "🥂", "🍾", "😄", "👏", "💪"
            ]
            return random.choice(exceeded_pool)
        elif ratio >= 0.75:
            almost_pool = [
                "🙂", "👌", "👍", "😊", "🤗", "👏", "😌", "😃",
                "💪", "🤩", "🎈", "😏", "😀", "😄", "🥰", "💖",
                "🌞", "🌈", "😇", "😁"
            ]
            return random.choice(almost_pool)
        elif ratio >= 0.5:
            halfway_pool = [
                "😐", "🤨", "🤔", "☕", "😕", "😑", "😬", "😶",
                "😟", "🧐", "🤷‍♂️", "🤷‍♀️", "😒", "🙄", "😔", "😓",
                "🤦‍♂️", "🤦‍♀️", "😮"
            ]
            return random.choice(halfway_pool)
        else:
            struggling_pool = [
                "😢", "😟", "😩", "😪", "😭", "🙁", "😞", "😓",
                "😔", "☹️", "😖", "😣", "😿", "🥺", "💔", "😫", "😢", "😩"
            ]
            return random.choice(struggling_pool)


    def draw_progress_bar(self, parent, ratio, expected, logged):
        """
        Draws a small horizontal progress bar showing ratio progress,
        with a label above it that displays the difference (logged - expected).
        The difference is colored red if negative, green if positive, and black if zero.
        """
        bar_width = 95
        bar_height = 8

        # Calculate the difference and choose a color.
        diff = logged - expected
        if diff > 0:
            diff_color = "green"
        elif diff < 0:
            diff_color = "red"
        else:
            diff_color = "black"

        # Container for both diff label and progress bar.
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(pady=(5, 0))

        # Create and pack the difference label above the progress bar.
        diff_label = tk.Label(
            container,
            text=f"{diff:+d} min",  # plus sign for positive values
            fg=diff_color,
            font=FONT_SMALL,
            bg=parent.cget("bg")
        )
        diff_label.pack(side="top", pady=(0, 2))

        # Create a canvas to draw the progress bar.
        canvas = tk.Canvas(container, width=bar_width, height=bar_height, highlightthickness=0)
        canvas.pack(side="top")

        # Draw the background of the progress bar.
        canvas.create_rectangle(0, 0, bar_width, bar_height, fill="#cccccc", width=0)

        # Calculate filled portion.
        fill_ratio = min(max(ratio, 0.0), 1.0)  # Clamp between 0 and 1
        fill_width = int(bar_width * fill_ratio)
        canvas.create_rectangle(0, 0, fill_width, bar_height, fill="#4CAF50", width=0)  # Green fill


    def prev_week(self):
        self.current_week_start -= datetime.timedelta(weeks=1)
        self.render_week()

    def next_week(self):
        self.current_week_start += datetime.timedelta(weeks=1)
        self.render_week()

    def refresh_week_view(self):
        """Re-renders the week view with updated data."""
        self.render_week()