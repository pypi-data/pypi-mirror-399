"""Keyword loader for dynamically importing keyword modules."""

import importlib.util
import logging
import pathlib
import sys

logger = logging.getLogger(__name__)


def load_keywords(folder: str = "examples") -> int:
    """Load keyword modules from a specified folder.

    Dynamically imports all Python files in the folder, which triggers
    the @keyword decorators to register the functions.

    Args:
        folder: Path to folder containing keyword files (default: "examples")

    Returns:
        Number of modules successfully loaded

    Example:
        # Load from default examples folder
        load_keywords()

        # Load from custom folder
        load_keywords("my_keywords")
        load_keywords("/path/to/keywords")
    """
    path = pathlib.Path(folder)

    if not path.exists():
        logger.warning(
            f"Keywords folder '{folder}' does not exist. No keywords loaded."
        )
        return 0

    # Ensure the folder is in sys.path for imports
    folder_abs = str(path.absolute())
    if folder_abs not in sys.path:
        sys.path.insert(0, folder_abs)

    loaded_count = 0

    for py_file in path.glob("*.py"):
        if py_file.name.startswith("_"):
            continue  # Skip __init__.py and private files

        module_name = py_file.stem

        try:
            # Load module from file path directly
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                logger.info(f"Loaded keyword module: {module_name}")
                loaded_count += 1
        except Exception as e:
            logger.error(f"Failed to load keyword module '{module_name}': {e}")

    logger.info(f"Loaded {loaded_count} keyword module(s) from '{folder}'")
    return loaded_count
