from pathlib import Path


def rename_bak_paths(path: Path, bakfix: str = "bak") -> None:
    """Переименовать bak-каталог или bak-файл"""

    n = 1

    # Найдём самый большой n
    while True:
        if path.is_dir():
            bak_path = path.parent / f"{path.name}-{bakfix}-{n}"
        else:
            bak_path = path.parent / f"{path.stem}-{bakfix}-{n}{path.suffix}"

        if bak_path.exists():
            n += 1
        else:
            n -= 1
            break

    if n > 0:
        # Переименуем bak-пути
        for k in range(n, 0, -1):
            if path.is_dir():
                (path.parent / f"{path.name}-{bakfix}-{k}").rename(
                    (path.parent / f"{path.name}-{bakfix}-{k + 1}")
                )
            else:
                (path.parent / f"{path.stem}-{bakfix}-{k}{path.suffix}").rename(
                    (path.parent / f"{path.stem}-{bakfix}-{k + 1}{path.suffix}")
                )

    if path.is_dir():
        path.rename(path.parent / f"{path.name}-{bakfix}-1")
    else:
        path.rename(path.parent / f"{path.stem}-{bakfix}-1{path.suffix}")
