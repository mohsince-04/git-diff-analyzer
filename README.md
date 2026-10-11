The **Code Reviewer & Bug Explainer CLI** is an automated code review and static analysis tool built for developers.

![Summary](https://github.com/user-attachments/assets/4ace0426-3884-4db0-adbf-408786d65bb7 "Note: Ignore vepython, it's just an alias.")


Instead of manually hunting for security flaws, performance anti-patterns, or logic bugs in a pull request, this tool ingests a code diff or patch (such as a `git diff` output), sends it to **Gemini 2.5 Flash**, and performs a rigorous architectural and security inspection. It returns a structured report featuring a code health score, severity-graded bug explanations, and syntax-highlighted refactoring code patches.

---

### Breakdown of Each File

The project consists of three main components:

#### 1. `schemas.py` (The Data Contract & Output Schema)

This file uses **Pydantic V2** to define the exact data structures enforced on the Gemini API response. By passing these models into `response_schema`, it guarantees that the output will return cleanly typed and structured JSON every single time.

* **`CodeIssue`**: Represents an individual bug or code smell, capturing its `severity` (Critical, Warning, Info), `issue_type`, approximate `line_number_approximate`, and a detailed `description`.
* **`RefactorSuggestion`**: Contains a clean `title`, the `improved_code` snippet, and the `rationale` for why the fix is superior.
* **`CodeReviewReport`**: The root model wrapping an `overall_health_score`, an executive `summary`, a list of detected `issues`, and actionable `refactorings`.

---

#### 2. `reviewer.py` (The Core CLI Execution Engine)

This script manages file parsing, command-line argument routing, Gemini API communication, error handling, and terminal rendering.

* **File & Diff Extraction:** Checks if the target input is a file path and reads its content, or treats it as an inline diff string.
* **Gemini API Integration:** Submits the diff to `gemini-2.5-flash` with a principal software engineer system prompt and strict JSON schema enforcement.
* **Stderr Suppression:** Temporarily redirects `sys.stderr` to `os.devnull` during the API call to eliminate background SDK warnings and keep your terminal output clean.
* **Rich Terminal UI & Syntax Highlighting:** Uses Python's `rich` library to render scorecards, severity color-coded issue panels, and **Monokai-themed syntax highlighting** for suggested code patches.

---

#### 3. `requirements.txt` & Supporting Files

* **`requirements.txt`**: Contains the dependency list (`google-genai`, `pydantic`, `typer`, `rich`) required to run the application.
* **`sample.diff`**: A sample patch file containing intentional security vulnerabilities (such as SQL injection patterns) used for testing and demonstration.
