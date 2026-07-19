# Contributing Guidelines

Thank you for considering contributing to the Git Worktree Management Tool (`gwt`)! This document provides guidelines for setting up your local environment, running the tests, and submitting changes.

---

## 1. Development Setup

To modify this tool locally:

1. Clone the repository:
   ```bash
   git clone git@github.com:jlothian/worktree-tool.git
   cd worktree-tool
   ```

2. (Optional) Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install development dependencies (like `ruff` for code styling):
   ```bash
   pip install ruff
   ```

---

## 2. Coding Standards and Code Formatting

We use `ruff` to enforce code quality and consistent formatting across Python files.

* **Linting Checks**:
  Verify code quality and clean up unused imports or statements:
  ```bash
  ruff check bin/gwt-cli tests/test_gwt.py
  ```
  To automatically apply fixes:
  ```bash
  ruff check bin/gwt-cli tests/test_gwt.py --fix
  ```

* **Formatting Checks**:
  To verify files are correctly styled:
  ```bash
  ruff format --check bin/gwt-cli tests/test_gwt.py
  ```
  To auto-format the files:
  ```bash
  ruff format bin/gwt-cli tests/test_gwt.py
  ```

---

## 3. Shell Script Validation

If you modify the shell integration helper (`aliases.sh`), run `shellcheck` to make sure there are no compatibility or syntax warnings across Bash/Zsh:

```bash
shellcheck aliases.sh
```

---

## 4. Running the Test Suite

We maintain an integration test suite under `tests/test_gwt.py` to ensure core commands (like `init`, `new`, `clean`, and `list`) function correctly across bare repository instances.

Run the test suite locally using the standard unittest discover tool:

```bash
python3 -m unittest discover -s tests
```

Ensure all tests pass before proposing a Pull Request.

---

## 5. Submitting Pull Requests

* Document your changes. If you add a feature, update the `docs/` and `README.md` files as necessary.
* Ensure CI checks (Python lint, Shellcheck, and tests) are green.
* Write clear, direct commit messages outlining what was changed and why.
