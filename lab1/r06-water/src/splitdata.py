from itertools import zip_longest
from pathlib import Path

def csv_read_rows(csv: Path) -> list[list[str]]:
    return [l.split(",") for l in csv.read_text().splitlines()]

def csv_read_cols(csv: Path) -> list[list[str]]:
    return [*zip_longest(*csv_read_rows(csv), fillvalue="")]  # type: ignore

def csv_write_rows(csv: Path, rows: list[list[str]]):
    csv.write_text("\n".join([",".join(row) for row in rows]))

def csv_write_cols(csv: Path, cols: list[list[str]]):
    csv_write_rows(csv, [*zip_longest(*cols, fillvalue="")])  # type: ignore

data = Path(__file__).parent.parent/"data"
cols = csv_read_cols(data/"cal.csv")
csv_write_cols(data/"longrun.csv", cols[8:10])  # cols {8, 9}
