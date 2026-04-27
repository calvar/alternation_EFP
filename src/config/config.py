from pathlib import Path

PATHS = {
    'patterns': Path(Path.cwd(), '..', 'data', 'patterns').resolve(),
    'graphs': Path(Path.cwd(), '..', 'data', 'graphs').resolve(),
    'html': Path(Path.cwd(), '..', 'data', 'html').resolve(),
    'simulation': Path(Path.cwd(), '..', 'data', 'simulation').resolve(),
}

# Check if the paths exist
for name, folder in PATHS.items():
    folder.mkdir(parents=True, exist_ok=True)