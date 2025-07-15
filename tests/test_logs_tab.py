from fusor.tabs.logs_tab import LogsTab

class DummyMainWindow:
    def __init__(self):
        self.auto_refresh_secs = 12
    def refresh_logs(self):
        pass


def test_timer_interval(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    assert tab._timer.interval() == 12000
    assert "12s" in tab.auto_checkbox.text()
