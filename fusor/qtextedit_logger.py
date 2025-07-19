from PyQt6.QtCore import QMetaObject, Qt, Q_ARG


class QTextEditLogger:
    def __init__(self, text_edit, original_stdout, echo=True):
        self.text_edit = text_edit
        self.original_stdout = original_stdout
        self.echo = echo

    def write(self, msg):
        if msg.rstrip():
            QMetaObject.invokeMethod(
                self.text_edit,
                "append",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msg.rstrip()),
            )
        if self.echo:
            self.original_stdout.write(msg)

    def flush(self):
        if self.echo:
            self.original_stdout.flush()
