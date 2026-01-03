# noxfile.py

import nox

# Define the Python versions to test against
PYTHON_VERSIONS = [ "3.13"]

# Set the default sessions to run when you just type "nox"
nox.options.sessions = ["lint", "mypy"]

@nox.session
def lint(session: nox.Session) -> None:
    """Run the linter (Ruff)."""
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session
def mypy(session: nox.Session) -> None:
    """Run the static type checker (MyPy)."""
    # Install the project itself in editable mode, along with test dependencies
    session.install("-e", ".[test]")
    session.run("mypy", "GeoTier")


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run the test suite with pytest."""
    session.install("-e", ".[test]")
    # The "{posargs}" allows you to pass extra arguments to pytest
    # Example: nox -s test -- -k "test_to_run"
    session.run("pytest", *session.posargs)


@nox.session
def docs(session: nox.Session) -> None:
    """Build the Sphinx documentation."""
    session.install("-e", ".[docs]")
    # Build the HTML documentation
    session.run("sphinx-build", "docs/source", "docs/build/html")
