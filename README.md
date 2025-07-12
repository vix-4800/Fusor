# Fusor

Fusor is a minimal PyQt6 application with a main window titled
**"Fusor – Laravel/PHP QA Toolbox"**. The main window contains a tabbed
interface with the following tabs:

- **Project** – buttons to manage migrations.
- **Git** – simple controls for common Git actions.
- **Database** – quick actions for opening and dumping a database.
- **Logs** – displays example log text with a refresh option.
- **Settings** – form fields for configuring the Git URL and other variables.

The widgets resize along with the main window so the interface stays usable at
any size.

## Running

Install the dependencies and execute `main.py`:

```bash
pip install PyQt6
python3 main.py
```
