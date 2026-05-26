# Contributing to CoshUI

Thanks for your interest in contributing to CoshUI! This document outlines 
the process for contributing and the conventions we follow.

> [!NOTE]
> CoshUI is primarily developed on [GitLab](https://gitlab.com/jylefv/CoshUI). Please open issues and pull requests there.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment and install dependencies:
```bash
pip install -e ".[all]"
```
4. Create a branch for your change:
```bash
git checkout -b prefix/branch-name develop
# or
git switch -c prefix/branch-name develop
```

> [!NOTE]
> Remember to always branch out of the `develop` branch.

## Branch Naming

Use the following prefixes:
- `fix/`: bug fixes
- `feature/`: new features
- `refactor/`: code cleanup with no behavior change
- `docs/`: fixed or added documentation to the code

## Code Style

- **Try not to have confusing abbreviations in variable names**: `center_x` not `cx`
- **Spaced colons**: (`{ "key" : value }` / `text : str`) not (`{"key": value}` / `text: str`)
- **Self documenting names**: code should read clearly without needing comments
- Comments should explain **why**, not **what**

> [!WARNING]
> The spaced colons style for CoshUI is purely for styling purposes (cause I like them) but it's not compliant with PEP 8 standards, 
> so if you have formatters while contributing to this project, make it ignore those warnings.

## Merge Requests

- One MR per issue
- Reference the issue in your MR description (`Fixes #N`)
- Keep changes focused and minimal

## Testing Your Changes

CoshUI is in its early stages, so our automated unit test suite is currently quite sparse. Because of this, **visual verification is our main defense** against bugs.

Before submitting your changes, please test them thoroughly:
* **Cross-Backend Checks:** Manually run your changes against **all** backends to ensure rendering is consistent.
* **Use Examples:** Run the scripts in the `/examples` directory (or create a temporary script) to visually inspect that the changed layout, alignment, and behavior work as expected.
* **Unit Tests (Optional but Awesome):** If you are comfortable writing automated tests, feel free to add them to the existing test file! It would be a massive help to the project.

## Reporting Bugs

Open an issue with:
- A clear description of the bug
- The approximate root cause if known 
- Explanation on how to replicate the bug if possible
- A potential fix if you have one
- A screenshot of UI and/or error traceback

## Feature Requests

Open an issue with:
- A description of the feature
- The proposed API if applicable
- The conditions and behavior

## Questions

Open an issue tagged `question` or reach out via the Discord.