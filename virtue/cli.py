from twisted.python.reflect import namedAny as named_any
import click
# Sigh. http://twistedmatrix.com/trac/ticket/8267
import twisted.trial.unittest
import twisted.trial.reporter

from virtue import __version__
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
        if Reporter is not None:
            return Reporter()
        try:
            return named_any(value)
        except Exception:
            raise click.BadParameter(
                "{0!r} is not a known reporter".format(value),
            )


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__, prog_name="virtue")
@click.option(
    "--reporter",
    default=ComponentizedReporter(),
    help="the name of a reporter to use for outputting test results",
    type=_Reporter(),
)
@click.argument("tests", nargs=-1)
@click.pass_context
def main(context, **kwargs):
    """
    virtue discovers and runs tests found in the given objects.

    Provide it with one or more tests (packages, modules or objects) to run.

    """

    result = run(**kwargs)
    context.exit(not result.wasSuccessful())
