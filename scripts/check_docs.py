"""Check the lab's UTF-8 Markdown, fenced blocks and inline local links."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+).*?\1")
LINK = re.compile(
    r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]*)>|([^\s)\n]+))'
    r'(?:\s+"[^"\n]*")?\s*\)'
)


def check_file(path: Path, root: Path) -> list[str]:
    """Return actionable diagnostics without changing files or fetching URLs."""
    label = path.relative_to(root).as_posix()
    if not path.resolve().is_relative_to(root):
        return [f"{label}: arquivo fora da raiz permitida"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return [f"{label}: nao foi possivel ler o arquivo como UTF-8"]
    errors: list[str] = []
    opened: tuple[str, int, int] | None = None
    for number, line in enumerate(lines, 1):
        marker = FENCE.match(line)
        if opened:
            if (
                marker
                and marker[1][0] == opened[0]
                and len(marker[1]) >= opened[1]
                and not marker[2].strip()
            ):
                opened = None
            continue
        if marker:
            opened = (marker[1][0], len(marker[1]), number)
            continue
        prose = INLINE_CODE.sub("", line)
        for match in LINK.finditer(prose):
            target = match[1] if match[1] is not None else match[2]
            try:
                parsed = urlsplit(target)
            except ValueError:
                errors.append(f"{label}:{number}: destino de link invalido")
                continue
            if parsed.scheme in {"https", "http", "mailto", "tel"} or parsed.netloc:
                continue
            if parsed.scheme:
                errors.append(f"{label}:{number}: esquema de link nao suportado")
                continue
            if not parsed.path:  # In-page anchors are intentionally not validated.
                continue
            local_path = unquote(parsed.path)
            if local_path.startswith(("/", "\\")) or "\\" in local_path:
                errors.append(f"{label}:{number}: use um caminho relativo com barras /")
                continue
            destination = (path.parent / local_path).resolve()
            if not destination.is_relative_to(root):
                errors.append(f"{label}:{number}: link sai da raiz do repositorio")
            elif not destination.exists():
                errors.append(f"{label}:{number}: link local inexistente: {local_path}")
    if opened:
        errors.append(f"{label}:{opened[2]}: bloco de codigo sem fechamento")
    return errors


def check_repository(root: Path) -> tuple[list[Path], list[str]]:
    root = root.resolve()
    if not root.is_dir():
        return [], ["Raiz de documentacao inexistente"]
    files = sorted(root.glob("*.md"))
    docs = root / "docs"
    if docs.is_symlink():
        return files, ["docs: diretorio simbolico nao suportado"]
    if docs.is_dir():
        files.extend(sorted(docs.rglob("*.md")))
    if not files:
        return [], ["Nenhum arquivo Markdown encontrado"]
    errors = [error for path in files for error in check_file(path, root)]
    return files, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    files, errors = check_repository(args.root)
    for error in errors:
        print(error)
    if errors:
        print(f"FALHOU: {len(errors)} problema(s) em {len(files)} arquivo(s).")
        return 1
    print(f"OK: {len(files)} arquivos Markdown; links locais e blocos conferidos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
