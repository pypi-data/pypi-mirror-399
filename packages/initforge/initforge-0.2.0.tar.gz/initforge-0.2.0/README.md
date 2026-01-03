## 🚀 initforge

initforge is a lightweight CLI tool that helps you bootstrap Python projects instantly — without repeating the same setup steps every time.

It generates a clean project structure and a ready-to-use README.md, so you can focus on building instead of configuring.

## ✨ Features

- 📁 Auto-detects project name from current directory

- 🧱 Generates a clean Python project structure

- 📝 Auto-creates a helpful README.md

- 🐍 Conda-friendly environment instructions

- ⚡ Simple, transparent, no hidden magic

- 🖥️ Works on Windows & Linux

## 📦 Installation

Install directly from PyPI:
```bash
pip install initforge
```

## 🚀 Quick Start

Navigate to your project folder and run:
```bash
projinit init
```

You’ll be guided through a few simple prompts:

- Project name

- Conda environment name

- Python version

- Run command

- README overwrite confirmation

That’s it — your project is ready.

---

## 📁 Generated Structure (example)
```yaml
my_project/
├── src/my_project/
│   └── __init__.py
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── README.md
└── .gitignore
```

## 🛠️ Example Workflow
```yaml
conda create -n my_project python=3.10 -y
conda activate my_project
pip install -r requirements.txt
```

Then start building 🚀