# Fusor

Fusor is a minimal PyQt6 application with a main window titled
**"Fusor – Laravel/PHP QA Toolbox"**. The UI is organized into several tabs
that provide helper actions for typical PHP development tasks.

The interface now uses a dark theme defined in `fusor/main_window.py` and larger buttons for better visibility.
The Project tab places the **Start** and **Stop** buttons side by side for
quicker access, and other tabs feature taller buttons as well.

The application is split into small modules under the `fusor` package to make
the codebase easier to maintain. Each tab lives in its own file inside
`fusor/tabs` and the main window logic resides in `fusor/main_window.py`.

The available tabs are:

-   **Project** – buttons to manage migrations and run PHPUnit tests.
-   **Git** – simple controls for common Git actions.
-   **Database** – quick actions for opening and dumping a database.
-   **Docker** – helpers for building, pulling and inspecting containers.
-   **Logs** – shows your project's log file (Laravel only) with a refresh
    button and optional auto refresh.
-   **Settings** – manage multiple projects using an **Add** button and project
   selector. The tab also lets you choose the framework, PHP executable, Docker
   service name and the server port. When **Yii** is selected, a drop-down
   lets you choose between the **basic** or **advanced** application template.

The Logs tab also provides an **Auto refresh** checkbox to reload logs
automatically every few seconds.

The application stores your list of projects, the currently selected project,
PHP binary, framework, Yii template, Docker service name, server port and the
"use docker" setting in `~/.fusor_config.json`. These values are restored
automatically when the application starts.

## Running

Install the dependencies from `requirements.txt` and run the application using
the provided console script:

```bash
pip install -r requirements.txt
fusor
# or
python3 -m fusor
```

### Docker mode

Enable the **Use Docker** option in the Settings tab to run all PHP commands
inside your project's Docker containers. When enabled, actions such as running
PHPUnit or starting the development server are executed via `docker compose`.
Set the **PHP Service** field to the name of the service running PHP so
`docker compose exec` uses the correct container.
The Start and Stop buttons will run `docker compose up -d` and `docker compose
down` respectively.
The new **Docker** tab becomes active in this mode and lets you rebuild
images, pull updates, inspect container status, view logs and restart
services with a single click.

## Testing

Install pytest and run the test suite from the repository root. Tests run
headless automatically thanks to the `QT_QPA_PLATFORM=offscreen` environment
variable set in the CI workflow:

```bash
pip install pytest
pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
