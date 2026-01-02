import importlib


def load_class_from_string(path: str):
    """
    Dynamically loads a class object from a fully qualified string path (e.g., 'module.sub.ClassName').

    Args:
        path (str): The string path to the class.

    Returns:
        The class object (not an instance).

    Raises:
        ImportError: If the module or class cannot be found.
    """
    try:
        # 1. Split the path into module and class name
        module_name, class_name = path.rsplit(".", 1)

        # 2. Import the module
        module = importlib.import_module(module_name)

        # 3. Get the class from the module
        return getattr(module, class_name)

    except (ValueError, ImportError, AttributeError) as e:
        # Handle cases where the path is malformed, module not found,
        # or class not found within the module
        raise ImportError(
            f"Could not load class '{path}'. Check if the module and class exist and are spelled correctly. Original error: {e}"
        )
