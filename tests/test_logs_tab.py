from PyQt6.QtCore import Qt

from fusor.tabs.logs_tab import LogsTab


class DummyMainWindow:
    def refresh_logs(self):
        pass


def test_search_highlights_first_match(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    text = "foo bar foo"
    tab.log_view.setPlainText(text)
    tab.search_edit.setText("foo")

    qtbot.mouseClick(tab.search_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    cursor = tab.log_view.textCursor()
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    assert text[start:end] == "foo"
    assert start == text.find("foo")

