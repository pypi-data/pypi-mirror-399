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


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _ensure_file(path: Path, content: str = ""):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def generate_project_from_base(
    project_name: str,
    env_name: str,
    python_version: str,
    run_command: str,
    preset: dict,
    overwrite_readme: bool = True,
):
    root = Path.cwd()

    # -------- folders --------
    for folder in preset.get("folders", []):
        folder_path = root / folder.format(project_name=project_name)
        _ensure_dir(folder_path)

    # -------- files --------
    for file in preset.get("files", []):
        file_path = root / file.format(project_name=project_name)
        _ensure_file(file_path)

    # -------- gitignore --------
    _write(root / ".gitignore", _read(".gitignore.txt"), overwrite=False)

    # -------- requirements.txt --------
    req_path = root / "requirements.txt"
    if not req_path.exists() or not req_path.read_text().strip():
        requirements = preset.get("requirements", [])
        req_path.write_text("\n".join(requirements) + "\n", encoding="utf-8")

    # -------- README --------
    readme_template = _read("README.md.txt")
    readme = readme_template.format(
        project_name=project_name,
        env_name=env_name,
        python_version=python_version,
        run_command=run_command,
    )
    _write(root / "README.md", readme, overwrite=overwrite_readme)

    print("\n✔ Project structure created")
    print("✔ Preset applied successfully")
