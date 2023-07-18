from pathlib import Path
from tempfile import TemporaryDirectory
import os

import nox

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
DOCS = ROOT / "docs"
PACKAGE = ROOT / "virtue"


nox.options.sessions = []


def session(default=True, **kwargs):
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(**kwargs)(fn)

    return _session


@session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "pypy3"])
def tests(session):
    session.install(ROOT)
    if session.posargs and session.posargs[0] == "coverage":
        if len(session.posargs) > 1 and session.posargs[1] == "github":
            posargs = session.posargs[2:]
            github = os.environ["GITHUB_STEP_SUMMARY"]
        else:
            posargs, github = session.posargs[1:], None

        session.install("coverage[toml]")
        session.run("coverage", "run", *posargs, "-m", "virtue", PACKAGE)

        if github is None:
            session.run("coverage", "report")
        else:
            with open(github, "a") as summary:
                summary.write("### Coverage\n\n")
                summary.flush()  # without a flush, output seems out of order.
                session.run(
                    "coverage",
                    "report",
                    "--format=markdown",
                    stdout=summary,
                )
    else:
        session.run("virtue", *session.posargs, "virtue")


@session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "pypy3"])
def audit(session):
    session.install("pip-audit", ROOT)
    session.run("python", "-m", "pip_audit")


@session(tags=["build"])
def build(session):
    session.install("build", "twine")
    with TemporaryDirectory() as tmpdir:
        session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)
        session.run("twine", "check", "--strict", tmpdir + "/*")


@session()
def secrets(session):
    session.install("detect-secrets")
    session.run("detect-secrets", "scan", ROOT)


@session(tags=["style"])
def style(session):
    session.install("ruff")
    session.run("ruff", "check", ROOT)


@session()
def typing(session):
    session.install("mypy", "types-colorama", ROOT)
    session.run("mypy", "--config", PYPROJECT, PACKAGE)


@session(tags=["docs"])
@nox.parametrize(
    "builder",
    [
        nox.param(name, id=name)
        for name in [
            "dirhtml",
            "doctest",
            "linkcheck",
            "man",
            "spelling",
        ]
    ],
)
def docs(session, builder):
    session.install("-r", DOCS / "requirements.txt")
    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        argv = ["-n", "-T", "-W"]
        if builder != "spelling":
            argv += ["-q"]
        session.run(
            "python",
            "-m",
            "sphinx",
            "-b",
            builder,
            DOCS,
            tmpdir / builder,
            *argv,
        )


@session(tags=["docs", "style"], name="docs(style)")
def docs_style(session):
    session.install(
        "doc8",
        "pygments",
        "pygments-github-lexers",
    )
    session.run("python", "-m", "doc8", "--config", PYPROJECT, DOCS)


@session(default=False)
def bandit(session):
    session.install("bandit")
    session.run("bandit", "--recursive", PACKAGE)
