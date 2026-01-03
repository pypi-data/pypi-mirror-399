from pathlib import Path
from projinit.generator import generate_project_from_base


def ask(prompt, default=None):
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    return input(f"{prompt}: ").strip()


def init():
    cwd = Path.cwd()
    project_name = cwd.name

    print(f"📁 Detected project: {project_name}")

    env_name = ask("Conda env name", project_name)
    python_version = ask("Python version", "3.10")
    run_command = ask("Run command (e.g. streamlit run app.py)", "")
    overwrite = ask("Overwrite README.md? (y/n)", "y").lower() == "y"

    generate_project_from_base(
        project_name=project_name,
        env_name=env_name,
        python_version=python_version,
        run_command=run_command,
        overwrite_readme=overwrite,
    )

    print("✅ projinit init completed")
