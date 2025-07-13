# Fusor

Fusor is a minimal PyQt6 application with a main window titled
**"Fusor – Laravel/PHP QA Toolbox"**. The UI is organised into several tabs
that provide helper actions for typical PHP development tasks.

The application is split into small modules under the `fusor` package to make
the codebase easier to maintain. Each tab lives in its own file inside
`fusor/tabs` and the main window logic resides in `fusor/main_window.py`.

The available tabs are:

-   **Project** – buttons to manage migrations and run PHPUnit tests.
-   **Git** – simple controls for common Git actions.
-   **Database** – quick actions for opening and dumping a database.
-   **Logs** – shows your project's log file (Laravel only) with a refresh option.
-   **Settings** – fields for selecting the project directory, framework and PHP executable.
    Browse buttons let you choose each path.

The application stores your selected project path, PHP binary and framework in
`~/.fusor_config.json`. These values are restored automatically when the
application starts.

## Running

Install the dependencies and execute `main.py`:

```bash
pip install PyQt6
python3 main.py
```
