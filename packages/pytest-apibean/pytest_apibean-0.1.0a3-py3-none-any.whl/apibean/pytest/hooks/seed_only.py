import pytest

_seed_only_done = False
_seed_only_item_nodeid = None

def pytest_runtest_call(item):
    global _seed_only_done, _seed_only_item_nodeid

    config = item.session.config

    if not config.option.apibean_seed_only:
        return

    # Once seeding has finished, skip the rest of the tests
    if _seed_only_done:
        if item.session.testscollected > 1:
            pytest.exit(
                "Seed-only completed for first test case",
                returncode=0,
            )

    # Only the first test reaches this point
    _seed_only_done = True
    _seed_only_item_nodeid = item.nodeid

    pytest.skip(
        "Test execution skipped after seeding (--apibean-seed-only)"
    )

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not config.option.apibean_seed_only:
        return

    terminalreporter.write_sep(
        "-",
        "Apibean seed-only mode: test execution skipped"
    )
