# Contributing to CoshUI

Thanks for your interest in contributing to CoshUI! This document outlines 
the process for contributing and the conventions we follow.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment and install dependencies:
```bash
pip install -e ".[pygame,raylib]"
```
4. Create a branch for your change:
```bash
git checkout -b fix/your-fix-name
```

## Branch Naming

Use the following prefixes:
- `fix/`: bug fixes
- `feature/`: new features
- `refactor/`: code cleanup with no behavior change

## Code Style

- **Try not to have confusing abbreviations in variable names**: `center_x` not `cx`
- **Spaced colons**: (`{ "key" : value }` / `text : str`) not (`{"key": value}` / `text: str`)
- **Self documenting names**: code should read clearly without needing comments
- Comments should explain **why**, not **what**

> [!WARNING]
> The spaced colons style for CoshUI is purely for styling purposes (cause I like them) but it's not compliant with PEP 8 standards, 
> so if you have formatters while contributing to this project, make it ignore those warnings.

## Pull Requests

- One PR per issue
- Reference the issue in your PR description (`Fixes #N`)
- Keep changes focused and minimal
- Test your changes against both Pygame and Raylib backends or wherever relevant

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