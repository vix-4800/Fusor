# Fusor

Fusor is a minimal PyQt6 application with a main window titled
**"Fusor – Laravel/PHP QA Toolbox"**. The UI is organized into several tabs
that provide helper actions for typical PHP development tasks.

![Main window with tabs](docs/screenshot.jpg)

An **About** dialog with the project's name, author and version is available
via the **Help** button in the top-right corner.

The interface now uses a dark theme defined in `fusor/main_window.py` and larger buttons for better visibility.
The Project tab places the **Start** and **Stop** buttons side by side for
quicker access, and other tabs feature taller buttons as well.

The application is split into small modules under the `fusor` package to make
the codebase easier to maintain. Each tab lives in its own file inside
`fusor/tabs` and the main window logic resides in `fusor/main_window.py`.

The available tabs are:

-   **Project** – buttons to manage migrations and run PHPUnit tests.
-   **Git** – simple controls for common Git actions and switching between local and remote branches.
-   **Database** – quick actions for opening and dumping a database.
-   **Docker** – helpers for building, pulling and inspecting containers.
-   **Logs** – shows your project's log file (Laravel only) with a refresh
    button and optional auto refresh.
-   **Settings** – manage multiple projects using an **Add** button and project
    selector. The tab also lets you choose the framework, PHP executable, Docker
    service name and the server port. When **Yii** is selected, a drop-down
    lets you choose between the **basic** or **advanced** application template.

The Logs tab also provides an **Auto refresh** checkbox to reload logs
automatically every few seconds. The interval can be customized in the
Settings tab via the **Auto refresh (seconds)** field.

The application stores your list of projects and, for each project, its own
settings such as PHP binary, Docker compose files, container name and server
port in `~/.fusor_config.json` under the `project_settings` key. The currently
selected project is remembered as well, and switching the active project
refreshes the Settings tab automatically so everything is restored when the
application starts.

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
down` respectively. If your project uses a non-default compose file you can
enter its path in **Compose Files**. Multiple files may be separated with
semicolons and will be passed as `-f` options to all compose commands.
The **Docker** tab only appears in this mode and lets you rebuild images,
pull updates, inspect container status, view logs and restart services with a
single click.

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
