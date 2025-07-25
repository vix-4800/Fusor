# Fusor

[![Tests](https://github.com/vix-4800/Fusor/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/vix-4800/Fusor/actions/workflows/tests.yml)

**Fusor** is a cross-platform desktop app built with PyQt6 that helps you manage PHP-based projects without touching the terminal. It’s designed for QA engineers, testers, junior developers, and anyone who wants to execute common project tasks with a click.

![Main window with tabs](docs/screenshot.png)

---

## Project Goals

Fusor aims to **simplify routine PHP project operations** via a user-friendly visual interface. It’s especially useful for:

-   QA and manual testers who want to run tests or inspect logs
-   Developers switching between projects or frameworks
-   Teams using Docker, Laravel, Yii, or plain PHP setups

---

## Features

-   Support for **Laravel**, **Yii**, and plain PHP setups
-   **Dark mode** with a modern UI
-   Project switching and per-project settings
-   Optional **Docker mode** for containerized workflows
-   Git, database, and migration helpers
-   Basic Node/NPM commands with automatic buttons for package scripts
-   Detects **Makefiles** and provides buttons for each target
-   Configurable log viewer with auto-refresh
-   **Ctrl+S** shortcut to quickly save settings
-   Isolated settings stored in `~/.fusor_config.json`

---

## Tab Overview

| Tab          | Description                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------- |
| **Project**  | Start/stop server and PHP tools (PHPUnit, Rector, CS-Fixer)                                    |
| **Git**      | Switch branches, view status or diff, pull, hard reset, stash changes                          |
| **Database** | Dump or restore SQL, run migrations, seed data                                                 |
| **Laravel**  | Migrate, rollback, fresh seed, and other artisan helpers _(visible when framework is Laravel)_ |
| **Symfony**  | Clear cache and manage Doctrine migrations _(visible when framework is Symfony)_               |
| **Yii**      | Common Yii console commands _(visible when framework is Yii)_                                  |
| **Docker**   | Build, pull, restart services, open shell, inspect containers _(visible only in Docker mode)_  |
| **Composer** | Run composer install/update/outdated and scripts                                               |
| **Node**     | Run npm install and package scripts (e.g., dev, build)                                         |
| **Make**     | Run make targets detected from the project's Makefile _(visible when Makefile present)_        |
| **Logs**     | View logs with optional auto-refresh and open log files in your default application            |
| **.env**     | Edit the project's environment file                                                            |
| **Terminal** | Embedded terminal for custom commands                                                          |
| **Settings** | Configure projects, PHP path, Docker options, and other preferences                            |

---

## Quick Start

1. Ensure **Python 3.10 or newer** is installed.

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python -m fusor
```

4. Add your project via **Settings** -> **Add Project** or **Clone Project**.
   When no projects exist, the Welcome dialog will prompt you to add or clone one.

Set the `APP_NAME` environment variable to customize the window title:

```bash
APP_NAME="My App" python -m fusor
```

---

## 🐳 Docker Mode

Enable the **Use Docker** option in the Settings tab to run commands inside your project's Docker containers.

-   Set **PHP Service** to match the container name in your `docker-compose.yml`
-   Support for multiple Compose files (separated by `;`)
-   Optional Compose profile via **Compose Profile** field
-   Set **Docker Project Path** if the code lives at a different path inside the container (default `/app`)
-   The **Docker** tab will appear automatically

Start/Stop buttons execute `docker compose up -d` and `docker compose down` (with `--profile` if specified) accordingly.

---

## Testing

Install the development dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

PyQt6 and pytest-qt are required for running the tests. Headless testing is supported by setting `QT_QPA_PLATFORM=offscreen`, already handled in the GitHub Actions workflow.

---

## Contributing

You're welcome to contribute!

-   Fork the repo
-   Create a new branch
-   Add your feature or fix
-   Submit a pull request

Ideas for UI improvements, framework support, or new tabs are always appreciated.

---

## License

This project is licensed under the [MIT License](LICENSE).
