import os

# Ensure Qt operates in offscreen mode during tests
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
