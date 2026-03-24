from pathlib import Path
import shutil, re

if __name__ == "__main__":
    # sp = Path("../.venv3/lib/python3.12/site-packages")
    sp = Path(__file__).parent / ".venv_gameEngine_build" / "Lib" / "site-packages"

    src = next(sp.glob("phonemizer_fork-*.dist-info"))
    dst = sp / src.name.replace("phonemizer_fork", "phonemizer")

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    meta = dst / "METADATA"
    txt = meta.read_text(encoding="utf-8")
    txt = re.sub(r"^Name:\s*phonemizer-fork\s*$", "Name: phonemizer", txt, flags=re.MULTILINE)
    meta.write_text(txt, encoding="utf-8")

    print(f"Created alias metadata: {dst}")