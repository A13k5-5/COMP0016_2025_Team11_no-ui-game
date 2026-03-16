import inspect


def patched_get_docstring_indentation_level(func):
    if inspect.isclass(func):
        return 4

    try:
        source = inspect.getsource(func)
        first_line = source.splitlines()[0]
        function_def_level = len(first_line) - len(first_line.lstrip())
        return 4 + function_def_level
    except OSError:
        return 4


def apply_patches():
    """Apply all necessary patches for Nuitka compatibility."""
    try:
        from transformers.utils import doc
        doc.get_docstring_indentation_level = patched_get_docstring_indentation_level
        print(
            "[PATCH] Successfully patched transformers.utils.doc.get_docstring_indentation_level")
        return True
    except Exception as e:
        print(f"[PATCH] Warning: Could not patch transformers: {e}")
        return False
