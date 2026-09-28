import json
import os
from datetime import datetime

APP_FOLDER_NAME = "ContadorRegressivo"
STATE_FILENAME = "state.json"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _state_file_path() -> str:
    """
    Salva o estado em %APPDATA%\\ContadorRegressivo\\state.json — a pasta
    correta para dados de usuário no Windows (diferente da pasta do .exe,
    que pode estar em um local sem permissão de escrita, como Program Files).
    """
    appdata = os.getenv("APPDATA", os.path.expanduser("~"))
    folder = os.path.join(appdata, APP_FOLDER_NAME)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, STATE_FILENAME)


def save_state(target: datetime) -> None:
    data = {"target": target.strftime(DATETIME_FORMAT)}

    with open(_state_file_path(), "w", encoding="utf-8") as file:
        json.dump(data, file)


def load_state() -> datetime | None:
    path = _state_file_path()

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return datetime.strptime(data["target"], DATETIME_FORMAT)

    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        # Arquivo corrompido ou em formato inesperado: ignora e trata
        # como se não houvesse contagem salva.
        return None


def clear_state() -> None:
    path = _state_file_path()

    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass