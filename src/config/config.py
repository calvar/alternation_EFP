from pathlib import Path

PATHS = {
    'patterns': Path(Path.cwd(), '..', 'data', 'patterns').resolve(),
    'graphs': Path(Path.cwd(), '..', 'data', 'graphs').resolve(),
}

# Chech if the paths exist
for name, folder in PATHS.items():
    folder.mkdir(parents=True, exist_ok=True)