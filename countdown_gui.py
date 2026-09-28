import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import pystray
from PIL import Image

import app_state
import windows_startup
from countdown_logic import CountdownTimer

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


def resource_path(*relative_path):
    """
    Returns the correct file path when running with
    'python countdown_gui.py' or inside a PyInstaller executable.
    """
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

        # Window icon (relogio.png must be in the same folder as the script/.exe)
        try:
            self.icon_image = tk.PhotoImage(file=resource_path("relogio.png"))
            self.root.iconphoto(False, self.icon_image)
        except tk.TclError:
            pass

        self.countdown = CountdownTimer()
        self.running = False
        self.alarm_triggered = False

        self._build_config_screen()
        self._build_countdown_screen()
        self._build_current_clock()

        # Fechar a janela (botão X) esconde o app em vez de encerrar o processo
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.tray_icon = None
        self._setup_tray_icon()

        # Se havia uma contagem salva de uma execução anterior, retoma ela.
        # Só mostra a tela de configuração do zero se não houver nada salvo.
        if not self._resume_saved_countdown():
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

        tk.Label(
            self.countdown_screen,
            text="Fechar a janela mantém a contagem rodando em segundo plano.",
            font=("Segoe UI", 9),
            fg="gray"
        ).pack(
            pady=(10, 0)
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

    # Bandeja do sistema (system tray)
    def _setup_tray_icon(self):
        try:
            tray_image = Image.open(resource_path("relogio.png"))
        except FileNotFoundError:
            tray_image = None

        menu = pystray.Menu(
            pystray.MenuItem("Abrir", self._restore_window, default=True),
            pystray.MenuItem("Sair", self._exit_app),
        )

        self.tray_icon = pystray.Icon(
            "ContadorRegressivo",
            tray_image,
            "Contador Regressivo",
            menu,
        )

        threading.Thread(
            target=self.tray_icon.run,
            daemon=True,
        ).start()

    def minimize_to_tray(self):
        self.root.withdraw()

    # Chamado pela thread do pystray -> repassa para a thread principal do Tkinter
    def _restore_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def _exit_app(self, icon=None, item=None):
        if self.tray_icon is not None:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    # Persistência: retomar contagem salva de uma execução anterior
    def _resume_saved_countdown(self) -> bool:
        saved_target = app_state.load_state()

        if saved_target is None:
            return False

        self.countdown.restore_target(saved_target)
        self._go_to_countdown_screen()
        return True

    def _go_to_countdown_screen(self):
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

    # Screen events
    def start(self):
        # Reseta o fundo de ambos os campos para branco antes de validar
        self.date_entry.config(bg="white")
        self.time_entry.config(bg="white")

        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()

        # Validação individual da data
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            self.date_entry.config(bg="#ffcccc")
            messagebox.showerror(
                "Data inválida",
                "A data deve estar no formato dd/mm/aaaa e ser válida."
            )
            return

        # Validação individual da hora
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            self.time_entry.config(bg="#ffcccc")
            messagebox.showerror(
                "Hora inválida",
                "A hora deve estar no formato hh:mm (de 00:00 a 23:59)."
            )
            return

        # Validação lógica geral (ex: data no passado)
        try:
            self.countdown.set_target(date_str, time_str)
        except ValueError as error:
            self.date_entry.config(bg="#ffcccc")
            self.time_entry.config(bg="#ffcccc")
            messagebox.showerror(
                "Erro na contagem",
                str(error)
            )
            return

        app_state.save_state(self.countdown.target)
        windows_startup.register_startup()

        self._go_to_countdown_screen()

    def go_back(self):
        self.running = False

        app_state.clear_state()
        windows_startup.unregister_startup()

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
        # A contagem terminou: não faz sentido continuar salva nem
        # reabrir o app sozinho da próxima vez que o Windows ligar.
        app_state.clear_state()
        windows_startup.unregister_startup()

        self.root.deiconify()
        self.root.lift()

        if self.tray_icon is not None:
            try:
                self.tray_icon.notify(
                    "O tempo que você definiu chegou a zero.",
                    "Contador Regressivo",
                )
            except NotImplementedError:
                pass

        if HAS_SOUND:
            for _ in range(3):
                winsound.MessageBeep(
                    winsound.MB_ICONEXCLAMATION
                )

        messagebox.showinfo(
            "Tempo esgotado!",
            "O tempo que você definiu chegou a zero."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownGUI(root)
    root.mainloop()