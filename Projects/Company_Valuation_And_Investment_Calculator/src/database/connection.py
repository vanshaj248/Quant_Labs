from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "market_data.duckdb"

def get_connection():
    return duckdb.connect(str(DB_PATH))