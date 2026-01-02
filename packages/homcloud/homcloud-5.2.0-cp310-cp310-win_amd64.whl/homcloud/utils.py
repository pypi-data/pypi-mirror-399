def load_symbols(path):
    if path is None:
        return None

    symbols = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            symbols.append(line)
    return symbols
