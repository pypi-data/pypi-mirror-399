from pathlib import Path
import argparse

from projinit.generator import generate_project_from_base
from projinit.presets import get_preset, list_presets
from projinit.validators import validate_python_version, normalize_env_name


def init():
    root = Path.cwd()
    project_name = root.name

    # -------- CLI args (non-interactive support) --------
    parser = argparse.ArgumentParser(
        description="Initialize a Python project with a clean structure"
    )
    parser.add_argument(
        "--preset",
        help="Project preset (base / ml / streamlit)",
    )
    parser.add_argument(
        "--run",
        help="Run command (e.g. python app.py, streamlit run app.py)",
    )
    args = parser.parse_args()

    print(f"📁 Repo detected: {project_name}")

    # -------- preset selection --------
    presets = list_presets()

    if args.preset:
        preset_key = args.preset
        preset = get_preset(preset_key)
        print(f"\n✔ Using preset (flag): {preset_key}")
    else:
        print("\nSelect project type:")
        for i, key in enumerate(presets, start=1):
            label = get_preset(key)["name"]
            print(f"{i}) {label}")

        choice = input("Choice [1]: ").strip()

        try:
            index = int(choice) - 1 if choice else 0
            preset_key = presets[index]
        except (ValueError, IndexError):
            print("⚠️ Invalid choice. Using base preset.")
            preset_key = "base"

        preset = get_preset(preset_key)
        print(f"\n✔ Using preset: {preset_key}")

    # -------- other inputs --------
    python_version = input("Python version [3.10]: ").strip() or "3.10"
    python_version = validate_python_version(python_version)

    env_name = input(f"Conda env name [{project_name}]: ").strip()
    env_name = normalize_env_name(env_name, project_name)

    run_command = (
        args.run
        or input(f"Run command [{preset['default_run']}]: ").strip()
        or preset["default_run"]
    )

    overwrite = input("Overwrite README.md? (y/n) [y]: ").strip().lower()
    overwrite_readme = overwrite != "n"

    # -------- generate --------
    generate_project_from_base(
        project_name=project_name,
        env_name=env_name,
        python_version=python_version,
        run_command=run_command,
        preset=preset,
        overwrite_readme=overwrite_readme,
    )

    print("\nNext steps:")
    print(f"conda create -n {env_name} python={python_version} -y")
    print(f"conda activate {env_name}")
    print("pip install -r requirements.txt")
