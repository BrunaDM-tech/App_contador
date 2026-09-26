import os
import sys
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from countdown_logic import CountdownTimer


try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


def resource_path(*relative_path):
   
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.abspath(__file__))
    )

    return os.path.join(base_path, *relative_path)


class CountdownGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Contador Regressivo")
        self.root.geometry("530x320")
        self.root.resizable(False, False)

        try:
            self.icon_image = tk.PhotoImage(file=resource_path("relogio.png"))
            self.root.iconphoto(False, self.icon_image)
        except tk.TclError:
            # Se o ícone não for encontrado, o app continua funcionando normalmente
            pass
    
        self.countdown = CountdownTimer()
        self.running = False
        self.alarm_triggered = False

        self._build_config_screen()
        self._build_countdown_screen()
        self._build_current_clock()

        self.config_screen.pack(
            expand=True,
            fill="both"
        )

    # Configure date/time
    def _build_config_screen(self):
        self.config_screen = tk.Frame(
            self.root,
            padx=20,
            pady=20
        )

        tk.Label(
            self.config_screen,
            text="Até quando podemos contar?",
            font=("Segoe UI", 17, "bold")
        ).pack(
            pady=(0, 15)
        )

        date_frame = tk.Frame(
            self.config_screen
        )

        date_frame.pack(
            pady=5
        )

        tk.Label(
            date_frame,
            text="Data (dd/mm/aaaa):"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.date_entry = tk.Entry(
            date_frame,
            width=15
        )

        self.date_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        self.date_entry.insert(
            0,
            datetime.now().strftime("%d/%m/%Y")
        )

        tk.Label(
            date_frame,
            text="Hora (hh:mm):"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )

        self.time_entry = tk.Entry(
            date_frame,
            width=15
        )

        self.time_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=8
        )

        self.time_entry.insert(
            0,
            "00:00"
        )

        tk.Button(
            self.config_screen,
            text="Iniciar contagem",
            font=("Segoe UI", 11),
            command=self.start
        ).pack(
            pady=20
        )

    # Countdown screen
    def _build_countdown_screen(self):
        self.countdown_screen = tk.Frame(
            self.root,
            padx=20,
            pady=20
        )

        self.target_label = tk.Label(
            self.countdown_screen,
            text="",
            font=("Segoe UI", 12),
            fg="gray"
        )

        self.target_label.pack(
            pady=(0, 10)
        )

        self.time_label = tk.Label(
            self.countdown_screen,
            text="00:00:00:00",
            font=("Consolas", 32, "bold")
        )

        self.time_label.pack(
            pady=20
        )

        tk.Label(
            self.countdown_screen,
            text="dias : horas : min : seg",
            font=("Segoe UI", 13),
            fg="gray"
        ).pack()

        tk.Button(
            self.countdown_screen,
            text="Voltar / novo horário",
            command=self.go_back
        ).pack(
            pady=25
        )

    # Live clock displayed on both screens
    def _build_current_clock(self):
        self.current_clock_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 10),
            fg="gray"
        )

        self.current_clock_label.pack(
            side="bottom",
            pady=6
        )

        self._update_current_clock()

    def _update_current_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")

        self.current_clock_label.config(
            text=f"Agora: {current_time}"
        )

        self.root.after(
            1000,
            self._update_current_clock
        )

    # Screen events
    def start(self):
        try:
            self.countdown.set_target(
                self.date_entry.get(),
                self.time_entry.get()
            )

        except ValueError as error:
            messagebox.showerror(
                "Data inválida",
                str(error)
            )
            return

        self.alarm_triggered = False

        self.target_label.config(
            text=f"Contando até {self.countdown.formatted_target()}"
        )

        self.config_screen.pack_forget()

        self.countdown_screen.pack(
            expand=True,
            fill="both"
        )

        self.running = True

        self._update_countdown()

    def go_back(self):
        self.running = False

        self.countdown_screen.pack_forget()

        self.config_screen.pack(
            expand=True,
            fill="both"
        )

    def _update_countdown(self):
        if not self.running:
            return

        remaining = self.countdown.calculate_remaining()

        self.time_label.config(
            text=remaining.formatted()
        )

        if remaining.is_zero:

            if not self.alarm_triggered:
                self.alarm_triggered = True
                self._trigger_alarm()

            return

        self.root.after(
            1000,
            self._update_countdown
        )

    def _trigger_alarm(self):
        if HAS_SOUND:
            for _ in range(3):
                winsound.MessageBeep(
                    winsound.MB_ICONEXCLAMATION
                )

        messagebox.showinfo(
            "Tempo esgotado!",
            "O tempo que você definiu chegou ao fim."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownGUI(root)
    root.mainloop()