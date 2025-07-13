from PyQt6.QtCore import QMetaObject, Qt, Q_ARG

class QTextEditLogger:
    """Write stdout text to both the console and a QTextEdit widget."""

    def __init__(self, text_edit, original_stdout):
        """Initialize the logger.

        Parameters
        ----------
        text_edit : QTextEdit
            Widget that receives log output.
        original_stdout : IO
            Original stdout stream to mirror messages to.
        """
        self.text_edit = text_edit
        self.original_stdout = original_stdout

    def write(self, msg):
        """Write ``msg`` to both stdout and the QTextEdit widget."""
        if msg.rstrip():
            QMetaObject.invokeMethod(
                self.text_edit,
                "append",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, msg.rstrip()),
            )
        self.original_stdout.write(msg)

    def flush(self):
        """Flush the underlying stdout stream."""
        self.original_stdout.flush()
