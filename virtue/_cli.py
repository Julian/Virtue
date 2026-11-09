from pkgutil import resolve_name
from textwrap import dedent

import click

from virtue.reporters import (
    ComponentizedReporter,
    Counter,
    JSONOutputter,
    TreeOutputter,
)
from virtue.runner import run


class _Reporter(click.ParamType):
    name = "reporter"

    _BUILT_IN = {
        "default": ComponentizedReporter,
        "dots": ComponentizedReporter,
        "json": lambda: ComponentizedReporter(outputter=JSONOutputter()),
        "quiet": Counter,
        "tree": lambda: ComponentizedReporter(outputter=TreeOutputter()),
    }

    def convert(self, value, param, ctx):
        if not isinstance(value, str):
            return value

        Reporter = self._BUILT_IN.get(value)
        if Reporter is None:
            try:
                Reporter = resolve_name(value)
            except (ValueError, ImportError, AttributeError) as err:
                exc = click.BadParameter(f"{value!r} is not a known reporter")
                raise exc from err

        return Reporter()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))  # type: ignore[arg-type]
@click.version_option(prog_name="virtue")
@click.option(
    "--reporter",
    default="default",
    help=dedent(
        """
        the name of a reporter to use for outputting test results.
        Can either be a fully qualified object name (e.g.
        mypackage.MyReporter) or one of the builtin reporter names:
        """,
    )
    + ", ".join(_Reporter._BUILT_IN),
    type=_Reporter(),
)
@click.option(
    "-x",
    "--stop-after",
    default=None,
    count=True,
    help=(
        "stop the test run after unsuccessful results. May be "
        "repeated to stop after that many non-successes."
    ),
)
@click.argument("tests", nargs=-1)
@click.pass_context
def main(context, **kwargs):
    """
    `virtue` discovers and runs tests found in the given objects.

    Provide it with one or more tests (packages, modules or objects) to run.

    """
    result = run(**kwargs)
    context.exit(not result.testsRun or not result.wasSuccessful())
