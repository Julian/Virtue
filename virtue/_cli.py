from textwrap import dedent

from twisted.python.reflect import namedAny as named_any
import click
import twisted.trial.reporter

from virtue.reporters import ComponentizedReporter
from virtue.runner import run


class _Reporter(click.ParamType):

    name = "reporter"

    _BUILT_IN = {
        "bwverbose": twisted.trial.reporter.VerboseTextReporter,
        "default": ComponentizedReporter,
        "subunit": twisted.trial.reporter.SubunitReporter,
        "summary": twisted.trial.reporter.MinimalReporter,
        "text": twisted.trial.reporter.TextReporter,
        "timing": twisted.trial.reporter.TimingTextReporter,
        "tree": twisted.trial.reporter.TreeReporter,
        "verbose": twisted.trial.reporter.VerboseTextReporter,
    }

    def convert(self, value, param, ctx):
        if not isinstance(value, str):
            return value

        Reporter = self._BUILT_IN.get(value)
        if Reporter is None:
            try:
                Reporter = named_any(value)
            except Exception:
                raise click.BadParameter(f"{value!r} is not a known reporter")

        return Reporter()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(prog_name="virtue")
@click.option(
    "--reporter",
    default="default",
    help=dedent(
        """
        the name of a reporter to use for outputting test results.
        Can either be a fully qualified object name (e.g.
        mypackage.MyReporter) or one of the builtin reporter names:
        """
    ) + ", ".join(_Reporter._BUILT_IN),
    type=_Reporter(),
)
@click.option(
    "-x", "--stop-after",
    default=None,
    count=True,
    help=(
        "stop the test run after unsuccessful results. May be "
        "repeated to stop after that many non-successes."
    )
)
@click.argument("tests", nargs=-1)
@click.pass_context
def main(context, **kwargs):
    """
    virtue discovers and runs tests found in the given objects.

    Provide it with one or more tests (packages, modules or objects) to run.

    """

    result = run(**kwargs)
    context.exit(not result.testsRun or not result.wasSuccessful())
