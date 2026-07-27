"""backup.py - Backup automático de la base de datos SQLite."""
import os
import sys
import shutil
from datetime import datetime, timedelta

if os.environ.get("FERRETERIA_BASE_DIR"):
    _base = os.environ["FERRETERIA_BASE_DIR"]
elif getattr(sys, 'frozen', False):
    _base = os.path.dirname(sys.executable)
else:
    _base = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_base, "db", "ferreteria.db")
BACKUP_DIR = os.path.join(_base, "db", "backups")


def hacer_backup():
    """Copia la base de datos con timestamp. Devuelve la ruta del backup."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return None
    nombre = f"ferreteria_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = os.path.join(BACKUP_DIR, nombre)
    shutil.copy2(DB_PATH, destino)
    _limpiar_backups_antiguos()
    return destino


def _limpiar_backups_antiguos(dias=30):
    """Elimina backups con más de N días de antigüedad."""
    if not os.path.exists(BACKUP_DIR):
        return
    limite = datetime.now() - timedelta(days=dias)
    for archivo in os.listdir(BACKUP_DIR):
        if not archivo.endswith(".db"):
            continue
        ruta = os.path.join(BACKUP_DIR, archivo)
        fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta))
        if fecha_mod < limite:
            os.remove(ruta)


def listar_backups():
    """Devuelve lista de (nombre, fecha, tamaño_kb) de backups disponibles."""
    if not os.path.exists(BACKUP_DIR):
        return []
    resultado = []
    for archivo in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if not archivo.endswith(".db"):
            continue
        ruta = os.path.join(BACKUP_DIR, archivo)
        fecha = datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%d/%m/%Y %H:%M")
        tamaño = os.path.getsize(ruta) // 1024
        resultado.append((archivo, fecha, f"{tamaño} KB", ruta))
    return resultado


def restaurar_backup(ruta_backup):
    """Restaura la base de datos desde un backup. Hace backup del estado actual antes."""
    if not os.path.exists(ruta_backup):
        raise FileNotFoundError(f"El backup no existe: {ruta_backup}")
    # Guardar estado actual antes de restaurar
    hacer_backup()
    shutil.copy2(ruta_backup, DB_PATH)
