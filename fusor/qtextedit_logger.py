from PyQt6.QtCore import QMetaObject, Qt, Q_ARG


class QTextEditLogger:
    """Write stdout text to both the console and a QTextEdit widget."""

    def __init__(self, text_edit, original_stdout):
        self.text_edit = text_edit
        self.original_stdout = original_stdout

    def write(self, msg):
        if msg.rstrip():
            QMetaObject.invokeMethod(
                self.text_edit,
                "append",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msg.rstrip()),
            )
        self.original_stdout.write(msg)

    def flush(self):
        self.original_stdout.flush()
