import tkinter as tk
from tkinter import filedialog, messagebox
from gamePlayer import GamePlayer


class GamePlayerGUI:
    """Simple GUI to select a game file and start playing."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Story Game Player")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2b2b")

        self.selected_file = None
        self.game_player = GamePlayer()

        self._setup_ui()

    def _setup_ui(self):
        # Title label
        title_label = tk.Label(
            self.root,
            text="Interactive Story Game",
            font=("Helvetica", 16, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        )
        title_label.pack(pady=20)

        # File selection frame
        file_frame = tk.Frame(self.root, bg="#2b2b2b")
        file_frame.pack(pady=10)

        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#aaaaaa",
            width=35
        )
        self.file_label.pack()

        # Choose file button
        choose_btn = tk.Button(
            self.root,
            text="Choose File",
            font=("Helvetica", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            activeforeground="#ffffff",
            width=15,
            cursor="hand2",
            command=self._choose_file
        )
        choose_btn.pack(pady=10)

        # Continue button
        self.continue_btn = tk.Button(
            self.root,
            text="Continue",
            font=("Helvetica", 11, "bold"),
            bg="#3a7d3a",
            fg="#ffffff",
            activebackground="#4a8d4a",
            activeforeground="#ffffff",
            width=15,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._start_game
        )
        self.continue_btn.pack(pady=5)

    def _choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Game File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            # Show only filename, not full path
            filename = file_path.split("/")[-1]
            self.file_label.config(text=filename, fg="#ffffff")
            self.continue_btn.config(state=tk.NORMAL)

    def _start_game(self):
        if self.selected_file:
            self.root.destroy()
            self.game_player.playGame(self.selected_file)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GamePlayerGUI()
    app.run()