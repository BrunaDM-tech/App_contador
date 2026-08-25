import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from contador_logica import ContadorRegressivo

try:
    import winsound
    TEM_SOM = True
except ImportError:
    TEM_SOM = False


class ContadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador Regressivo")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        self.contador = ContadorRegressivo()
        self.rodando = False
        self.alarme_disparado = False

        self._montar_tela_config()
        self._montar_tela_contador()

        self.tela_config.pack(expand=True, fill="both")

    #  configurar data/hora
    def _montar_tela_config(self):
        self.tela_config = tk.Frame(self.root, padx=20, pady=20)

        tk.Label(self.tela_config, text="Contar até quando?",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))

        frame_data = tk.Frame(self.tela_config)
        frame_data.pack(pady=5)

        tk.Label(frame_data, text="Data (dd/mm/aaaa):").grid(row=0, column=0, sticky="w")
        self.entry_data = tk.Entry(frame_data, width=15)
        self.entry_data.grid(row=0, column=1, padx=5)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(frame_data, text="Hora (hh:mm):").grid(row=1, column=0, sticky="w", pady=8)
        self.entry_hora = tk.Entry(frame_data, width=15)
        self.entry_hora.grid(row=1, column=1, padx=5, pady=8)
        self.entry_hora.insert(0, "00:00")

        tk.Button(self.tela_config, text="Iniciar contagem",
                  font=("Segoe UI", 11), command=self.iniciar).pack(pady=20)

    #  contador rodando 
    def _montar_tela_contador(self):
        self.tela_contador = tk.Frame(self.root, padx=20, pady=20)

        self.label_alvo = tk.Label(self.tela_contador, text="",
                                    font=("Segoe UI", 10), fg="gray")
        self.label_alvo.pack(pady=(0, 10))

        self.label_tempo = tk.Label(self.tela_contador, text="00:00:00:00",
                                     font=("Consolas", 32, "bold"))
        self.label_tempo.pack(pady=20)

        tk.Label(self.tela_contador, text="dias : horas : min : seg",
                 font=("Segoe UI", 9), fg="gray").pack()

        tk.Button(self.tela_contador, text="Voltar / novo horário",
                  command=self.voltar).pack(pady=20)

    #  eventos da tela (chamam a lógica) 
    def iniciar(self):
        try:
            self.contador.definir_alvo(self.entry_data.get(), self.entry_hora.get())
        except ValueError as erro:
            messagebox.showerror("Data inválida", str(erro))
            return

        self.alarme_disparado = False
        self.label_alvo.config(text=f"Contando até {self.contador.alvo_formatado()}")

        self.tela_config.pack_forget()
        self.tela_contador.pack(expand=True, fill="both")

        self.rodando = True
        self._atualizar()

    def voltar(self):
        self.rodando = False
        self.tela_contador.pack_forget()
        self.tela_config.pack(expand=True, fill="both")

    def _atualizar(self):
        if not self.rodando:
            return

        restante = self.contador.calcular_restante()
        self.label_tempo.config(text=restante.formatado())

        if restante.zerado:
            if not self.alarme_disparado:
                self.alarme_disparado = True
                self._disparar_alarme()
            return

        self.root.after(1000, self._atualizar)

    def _disparar_alarme(self):
        if TEM_SOM:
            for _ in range(3):
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        messagebox.showinfo("Tempo esgotado!", "O tempo que você definiu chegou a zero.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ContadorGUI(root)
    root.mainloop()