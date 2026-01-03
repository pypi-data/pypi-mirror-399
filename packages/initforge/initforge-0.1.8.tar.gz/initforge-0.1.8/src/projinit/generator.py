from pathlib import Path
from importlib import resources


TEMPLATE_PACKAGE = "projinit"
TEMPLATE_BASE = ("templates", "base")


def _read(rel_path: str) -> str:
    """
    Read a template file from the installed package.
    Works for editable installs and PyPI installs.
    """
    return (
        resources.files(TEMPLATE_PACKAGE)
        .joinpath(*TEMPLATE_BASE, rel_path)
        .read_text(encoding="utf-8")
    )


def _write(path: Path, content: str, overwrite: bool = True):
    """
    Write content to a file.
    Creates parent directories if needed.
    Respects overwrite flag.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def generate_project_from_base(
    project_name: str,
    env_name: str,
    python_version: str,
    run_command: str,
    overwrite_readme: bool = True,
):
    # IMPORTANT: always operate on user's current directory
    root = Path.cwd()

    # --- src package structure ---
    _write(
        root / "src" / project_name / "__init__.py",
        "# package\n",
        overwrite=False,
    )

    # --- .gitignore (never overwrite existing) ---
    _write(
        root / ".gitignore",
        _read(".gitignore.txt"),
        overwrite=False,
    )

    # --- requirements.txt (preserve if exists) ---
    req = root / "requirements.txt"
    if not req.exists():
        req.write_text("", encoding="utf-8")

    # --- README.md ---
    readme_template = _read("README.md.txt")
    rendered_readme = (
        readme_template
        .replace("{project_name}", project_name)
        .replace("{env_name}", env_name)
        .replace("{python_version}", python_version)
        .replace("{run_command}", run_command or "# add run command")
    )

    _write(
        root / "README.md",
        rendered_readme,
        overwrite=overwrite_readme,
    )
