def pytest_report_teststatus(report):
    """
    Changes the words in the status report of the test and adds a UTF-8 symbol.
    """
    if report.when == 'call':
        if report.passed:
            letter = '\u2714'
            longrep = ' \u2714 '
        elif report.skipped:
            letter = 's'
            longrep = ' \u27A5 '
        elif report.failed:
            letter = '\u2717'
            longrep = ' \u2717 '
        return report.outcome, letter, report.outcome.upper() + longrep
