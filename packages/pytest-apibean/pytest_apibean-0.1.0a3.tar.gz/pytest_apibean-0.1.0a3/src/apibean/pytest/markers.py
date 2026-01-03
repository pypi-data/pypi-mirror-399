APIBEAN_MARKERS = {
    "seed": (
        "seed(name, **kwargs): "
        "Apply data seeders before test execution. "
        "Seed name must be in format 'module.variant'."
    ),
    "e2e": (
        "e2e: "
        "Mark a test as end-to-end. Usually slow. "
        "Intended for CI or full system validation. "
        "Runs with full infrastructure enabled."
    ),
    "e2e1": (
        "e2e1: "
        "Selected end-to-end tests that should be "
        "runnable quickly during development (fast lane)."
    ),
}
