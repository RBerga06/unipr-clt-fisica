from pathlib import Path

def merge(file1: Path, file2: Path, output: Path, sep: str = "\n") -> None:
    output.write_text(file1.read_text() + sep + file2.read_text())

DIR = Path(__file__).parent
merge(DIR/"dadi1.txt", DIR/"dadi2.txt", DIR/"dadi.txt", sep="# --- NEW DATA --- #\n")
