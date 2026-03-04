#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


FFMPEG_CANDIDATES = [
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
]


def find_ffmpeg() -> str | None:
    for candidate in FFMPEG_CANDIDATES:
        if Path(candidate).exists():
            return candidate

    return shutil.which("ffmpeg")


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Borstbindare Wenman")
        self.root.geometry("620x360")
        self.root.minsize(560, 320)
        self.root.configure(bg="#dbe5d7")

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Välj en MP4-fil för att börja.")
        self.busy = False
        self.ffmpeg_path = find_ffmpeg()

        self._build_ui()

        if not self.ffmpeg_path:
            self.status_text.set("ffmpeg hittades inte.")
            messagebox.showwarning(
                "Borstbindare Wenman",
                "ffmpeg hittades inte på datorn. Installera ffmpeg för att kunna konvertera.",
            )

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, bg="#dbe5d7", padx=24, pady=24)
        container.pack(fill="both", expand=True)

        title = tk.Label(
            container,
            text="Borstbindare Wenman",
            font=("Helvetica Neue", 28, "bold"),
            bg="#dbe5d7",
            fg="#1d2a1f",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            container,
            text="Native MP4 till WAV-konverterare för macOS",
            font=("Helvetica Neue", 13),
            bg="#dbe5d7",
            fg="#4d5d4f",
        )
        subtitle.pack(anchor="w", pady=(6, 18))

        panel = tk.Frame(
            container,
            bg="#f7f5ee",
            highlightbackground="#c9d2c5",
            highlightthickness=1,
            padx=18,
            pady=18,
        )
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="Källfil (MP4)",
            font=("Helvetica Neue", 12, "bold"),
            bg="#f7f5ee",
            fg="#1d2a1f",
        ).pack(anchor="w")

        input_row = tk.Frame(panel, bg="#f7f5ee")
        input_row.pack(fill="x", pady=(8, 16))

        self.input_entry = ttk.Entry(input_row, textvariable=self.input_path)
        self.input_entry.pack(side="left", fill="x", expand=True)

        self.input_button = ttk.Button(
            input_row, text="Välj MP4", command=self.choose_input_file
        )
        self.input_button.pack(side="left", padx=(10, 0))

        tk.Label(
            panel,
            text="Målfil (WAV)",
            font=("Helvetica Neue", 12, "bold"),
            bg="#f7f5ee",
            fg="#1d2a1f",
        ).pack(anchor="w")

        output_row = tk.Frame(panel, bg="#f7f5ee")
        output_row.pack(fill="x", pady=(8, 16))

        self.output_entry = ttk.Entry(output_row, textvariable=self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True)

        self.output_button = ttk.Button(
            output_row, text="Spara Som", command=self.choose_output_file
        )
        self.output_button.pack(side="left", padx=(10, 0))

        self.convert_button = ttk.Button(
            panel, text="Konvertera till WAV", command=self.start_conversion
        )
        self.convert_button.pack(anchor="w", pady=(4, 14))

        self.progress = ttk.Progressbar(panel, mode="indeterminate")
        self.progress.pack(fill="x")

        status = tk.Label(
            panel,
            textvariable=self.status_text,
            wraplength=520,
            justify="left",
            font=("Helvetica Neue", 12),
            bg="#f7f5ee",
            fg="#4d5d4f",
        )
        status.pack(anchor="w", pady=(14, 0))

    def choose_input_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Välj MP4-fil",
            filetypes=[("MP4-filer", "*.mp4"), ("Alla filer", "*.*")],
        )
        if not file_path:
            return

        self.input_path.set(file_path)

        if not self.output_path.get():
            suggested = str(Path(file_path).with_suffix(".wav"))
            self.output_path.set(suggested)

        self.status_text.set("MP4 vald. Välj målfil eller konvertera direkt.")

    def choose_output_file(self) -> None:
        initial = self.output_path.get() or "output.wav"
        file_path = filedialog.asksaveasfilename(
            title="Spara WAV-fil",
            defaultextension=".wav",
            initialfile=Path(initial).name,
            filetypes=[("WAV-filer", "*.wav")],
        )
        if not file_path:
            return

        self.output_path.set(file_path)
        self.status_text.set("Målfil vald. Redo att konvertera.")

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.input_button.config(state=state)
        self.output_button.config(state=state)
        self.convert_button.config(state=state)

        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def start_conversion(self) -> None:
        if self.busy:
            return

        if not self.ffmpeg_path:
            messagebox.showwarning(
                "Borstbindare Wenman",
                "ffmpeg hittades inte på datorn. Installera ffmpeg först.",
            )
            return

        input_value = self.input_path.get().strip()
        output_value = self.output_path.get().strip()

        if not input_value:
            messagebox.showwarning("Borstbindare Wenman", "Välj en MP4-fil först.")
            return

        if not output_value:
            messagebox.showwarning("Borstbindare Wenman", "Välj var WAV-filen ska sparas.")
            return

        input_file = Path(input_value)
        output_file = Path(output_value)

        if not input_file.exists():
            messagebox.showwarning("Borstbindare Wenman", "Den valda MP4-filen finns inte.")
            return

        if input_file.resolve() == output_file.resolve():
            messagebox.showwarning(
                "Borstbindare Wenman",
                "Källfil och målfil kan inte vara samma fil.",
            )
            return

        self.set_busy(True)
        self.status_text.set("Konverterar nu. Detta kan ta en stund.")

        thread = threading.Thread(
            target=self._run_conversion, args=(str(input_file), str(output_file)), daemon=True
        )
        thread.start()

    def _run_conversion(self, input_file: str, output_file: str) -> None:
        try:
            subprocess.run(
                [
                    self.ffmpeg_path,
                    "-y",
                    "-i",
                    input_file,
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    output_file,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as error:
            lines = error.stderr.decode("utf-8", "replace").strip().splitlines()
            message = lines[-1] if lines else "Konverteringen misslyckades."
            self.root.after(0, self._finish_with_error, message)
            return
        except Exception as error:  # pragma: no cover
            self.root.after(0, self._finish_with_error, str(error))
            return

        self.root.after(0, self._finish_success, output_file)

    def _finish_success(self, output_file: str) -> None:
        self.set_busy(False)
        self.status_text.set(f"Klar. WAV skapad: {output_file}")
        messagebox.showinfo("Borstbindare Wenman", "Konverteringen är klar.")

    def _finish_with_error(self, message: str) -> None:
        self.set_busy(False)
        self.status_text.set(f"Fel: {message}")
        messagebox.showerror("Borstbindare Wenman", message)


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure("TButton", padding=8)
    style.configure("TEntry", padding=6)

    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
