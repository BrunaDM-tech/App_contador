from datetime import datetime


class RemainingTime:

    def __init__(
        self,
        days: int,
        hours: int,
        minutes: int,
        seconds: int,
        is_zero: bool
    ):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.is_zero = is_zero

    def formatted(self) -> str:
        return (
            f"{self.days:02d}:"
            f"{self.hours:02d}:"
            f"{self.minutes:02d}:"
            f"{self.seconds:02d}"
        )


class CountdownTimer:

    def __init__(self):
        self.target: datetime | None = None

    def set_target(
        self,
        date_text: str,
        time_text: str
    ) -> None:

        try:
            target = datetime.strptime(
                f"{date_text.strip()} {time_text.strip()}",
                "%d/%m/%Y %H:%M"
            )

        except ValueError:
            raise ValueError(
                "Use o formato dd/mm/aaaa para a data e hh:mm para a hora."
            )

        if target <= datetime.now():
            raise ValueError(
                "Escolha uma data/hora no futuro."
            )

        self.target = target

    def restore_target(self, target: datetime) -> None:
        """
        Define o alvo diretamente, sem validação, usado ao retomar uma
        contagem salva anteriormente (o valor já foi validado quando o
        usuário definiu originalmente). Aceita datas no passado de propósito:
        é o caso de o PC ter ficado desligado além do horário previsto —
        nesse caso, queremos detectar 'já passou' e disparar o alarme,
        não rejeitar o valor.
        """
        self.target = target

    def formatted_target(self) -> str:

        if self.target is None:
            return ""

        return self.target.strftime(
            "%d/%m/%Y %H:%M"
        )

    def calculate_remaining(self) -> RemainingTime:

        if self.target is None:
            return RemainingTime(
                0,
                0,
                0,
                0,
                is_zero=True
            )

        total_seconds = int(
            (self.target - datetime.now()).total_seconds()
        )

        if total_seconds <= 0:
            return RemainingTime(
                0,
                0,
                0,
                0,
                is_zero=True
            )

        days, remainder = divmod(
            total_seconds,
            86400
        )

        hours, remainder = divmod(
            remainder,
            3600
        )

        minutes, seconds = divmod(
            remainder,
            60
        )

        return RemainingTime(
            days,
            hours,
            minutes,
            seconds,
            is_zero=False
        )