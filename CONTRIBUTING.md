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

- **Self documenting names**: Code should read clearly without fully needing comments.
- **Documentation**: If you want to add documentation for user exposed functions/types follow this example:
```python
"""
Description about the function or class that explains what it is and what it does

### Parameters (if it has parameters)

- **parameter_x**: Description about what it is and what it does.
- **parameter_y**: Description about what it is and what it does.

### Attributes (if it has attributes needed to be known or are altered by the user)

- **attribute_1**: What the attribute is, what it holds, and roughly what it does.
- **attribute_2**: What the attribute is, what it holds, and roughly what it does.

### Returns (if it has a return type)

- **return_type**: What it returns and anything the user has to know about it.
"""
```
Check the `animate()` function for a real example. 
- **PEP 8**: Just try to follow most [PEP 8](https://peps.python.org/pep-0008/) Standards (But truthfully, it's a convention. Even I'm not sure if I follow it all 😅).

## Merge Requests

- One MR per issue
- Reference the issue in your MR description (`Fixes #N`)
- Keep changes focused and minimal

## Testing Your Changes

CoshUI is in its early stages, so our automated unit test suite is currently quite sparse. Because of this, **visual verification is our main defense** against bugs.

Before submitting your changes, please test them thoroughly:
* **Cross-Backend Checks:** Manually run your changes against **all** backends to ensure rendering is consistent.
* **Debugger:** Use the debugger (accessed by passing `cui.DEBUG` to `CoshUIRenderer()`) to verify correct values and check CoshUI performance.
* **Use Examples:** Run the scripts in the `/examples` directory (or create a temporary script) to visually inspect that the changed layout, alignment, and behavior work as expected.
* **Unit Tests (Optional but Awesome):** If you are comfortable writing automated tests, feel free to add them to the existing test file! It would be a massive help to the project.

## Reporting Bugs

Open an issue with:
- A clear description of the bug
- The approximate root cause if known 
- Explanation on how to replicate the bug if possible
- A potential fix if you have one
- A screenshot of UI and/or error traceback

If you're still unsure, here's a guide (these should be followed in this exact order):
```markdown
### Description
Description of the bug.

### Root Cause 
What the cause of the bug is (if you know or is applicable).

### Potential Fix
An idea for a fix of the bug (optional but greatly appreciated).

### Relevant Code & Images / Examples
Helpful code or images that could help replicate the bug.
```

## Feature Requests

Open an issue with:
- A description of the feature
- The proposed API if applicable
- The conditions and behavior

## Questions

Open an issue tagged `question` or reach out via the Discord.