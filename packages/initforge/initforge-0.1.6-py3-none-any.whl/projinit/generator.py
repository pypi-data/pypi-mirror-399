from pathlib import Path

TEMPLATE_BASE = Path("projinit/templates/base")


def _read(rel):
    return (TEMPLATE_BASE / rel).read_text(encoding="utf-8")


def _write(path: Path, content: str, overwrite=True):
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
    root = Path.cwd()

    # ensure src structure
    _write(root / "src" / project_name / "__init__.py", "# package\n", overwrite=False)

    # ensure gitignore
    _write(root / ".gitignore", _read(".gitignore.txt"), overwrite=False)

    # ensure requirements.txt (keep existing)
    req = root / "requirements.txt"
    if not req.exists():
        req.write_text("", encoding="utf-8")

    # README (overwrite by choice)
    readme = _read("README.md.txt")
    readme = (
        readme
        .replace("{project_name}", project_name)
        .replace("{env_name}", env_name)
        .replace("{python_version}", python_version)
        .replace("{run_command}", run_command or "# add run command")
    )
    _write(root / "README.md", readme, overwrite=overwrite_readme)
