from datetime import datetime


class TempoRestante:

    def __init__(self, dias: int, horas: int, minutos: int, segundos: int, zerado: bool):
        self.dias = dias
        self.horas = horas
        self.minutos = minutos
        self.segundos = segundos
        self.zerado = zerado

    def formatado(self) -> str:
        return f"{self.dias:02d}:{self.horas:02d}:{self.minutos:02d}:{self.segundos:02d}"


class ContadorRegressivo:

    def __init__(self):
        self.alvo: datetime | None = None

    def definir_alvo(self, data_texto: str, hora_texto: str) -> None:
  
        try:
            alvo = datetime.strptime(f"{data_texto.strip()} {hora_texto.strip()}", "%d/%m/%Y %H:%M")
        except ValueError:
            raise ValueError("Use o formato dd/mm/aaaa para a data e hh:mm para a hora.")

        if alvo <= datetime.now():
            raise ValueError("Escolha uma data/hora no futuro.")

        self.alvo = alvo

    def alvo_formatado(self) -> str:
        if self.alvo is None:
            return ""
        return self.alvo.strftime("%d/%m/%Y %H:%M")

    def calcular_restante(self) -> TempoRestante:
        
        if self.alvo is None:
            return TempoRestante(0, 0, 0, 0, zerado=True)

        total_segundos = int((self.alvo - datetime.now()).total_seconds())

        if total_segundos <= 0:
            return TempoRestante(0, 0, 0, 0, zerado=True)

        dias, resto = divmod(total_segundos, 86400)
        horas, resto = divmod(resto, 3600)
        minutos, segundos = divmod(resto, 60)

        return TempoRestante(dias, horas, minutos, segundos, zerado=False)