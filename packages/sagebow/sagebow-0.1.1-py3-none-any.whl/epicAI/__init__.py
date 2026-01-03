"""SageBow public API surface (compat shim).
This package intentionally avoids loading environment files automatically
to reduce accidental exposure of secrets from local development setups.
"""
from .mini_notebook import run as _original_run
from .auth import get_current_user as _get_current_user
from .auth import logout as _logout
def _in_jupyter_with_widgets() -> bool:
    """Return True if running inside a Jupyter kernel with ipywidgets available."""
    try:
        from IPython import get_ipython  # type: ignore
        ip = get_ipython()
        if ip is None:
            return False
        shell = ip.__class__.__name__
        if shell != "ZMQInteractiveShell":
            return False
    except Exception:
        return False
    try:
        import ipywidgets as _w  # noqa: F401
    except Exception:
        return False
    return True
def _print_terminal_warning() -> None:
    """Let the user know SageBow is notebook-only."""
    banner = (
        "╔════════════════════════════════════════════╗\n"
        "║               Welcome to SageBow           ║\n"
        "╚════════════════════════════════════════════╝"
    )
    message = (
        "It looks like you're running SageBow from a terminal or IDE without Jupyter support.\n"
        "Open a Jupyter Notebook (.ipynb file) to access SageBow's agents.\n"
        "Most IDEs (VSCode, PyCharm, Spyder, etc.) have a Jupyter extension you can install."
    )
    print(banner)
    print()
    print(message)
def run(mode: str = "auto", api_key: str = None):
    """Start SageBow when running inside a supported Jupyter environment.
    Args:
        mode: Kept for backward compatibility. "notebook" forces the mini-notebook UI.
        api_key: Unused placeholder maintained for compatibility.
    """
    mode = (mode or "auto").lower().strip()
    if mode == "notebook":
        return _original_run()
    if _in_jupyter_with_widgets():
        return _original_run()
    _print_terminal_warning()
    return None
def get_current_user():
    return _get_current_user()
def logout():
    return _logout()
__all__ = ["run"]
if __name__ == "__main__":
    run()
