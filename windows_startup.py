import os
import sys

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    # winreg só existe no Windows; em outros sistemas o app simplesmente
    # não oferece a funcionalidade de abrir sozinho no login.
    HAS_WINREG = False

REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "ContadorRegressivo"


def _startup_command() -> str:
    """
    Monta o comando que o Windows deve executar no login.

    Quando empacotado como .exe (PyInstaller), sys.executable É o próprio
    ContadorRegressivo.exe. Rodando via 'python countdown_gui.py' (modo
    desenvolvimento), sys.executable é o interpretador Python,  incluído o caminho do script também.
    """
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    script_path = os.path.abspath(sys.argv[0])
    return f'"{sys.executable}" "{script_path}"'


def register_startup() -> None:
    if not HAS_WINREG:
        return

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        )

        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            _startup_command(),
        )

        winreg.CloseKey(key)

    except OSError:
        # Não foi possível registrar (permissão, chave ausente, etc).
        # A contagem continua funcionando normalmente, só não vai reabrir
        # sozinha se o PC for desligado.
        pass


def unregister_startup() -> None:
    if not HAS_WINREG:
        return

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        )

        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)

    except FileNotFoundError:
        # Já não estava registrado — nada a fazer.
        pass

    except OSError:
        pass