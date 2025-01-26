import logging
from time import time_ns,sleep
from .config import load_config
from .utils.logging import logger_config
import docopt_subcommands as dsc
from contextlib import contextmanager
from matplotlib import pyplot
from .audio.audio_clip import AudioClip

DOC_TEMPLATE = """{program}

Usage: {program} [options] <command> [<args> ...]

Options:
  -h --help     Show this screen.
  -v --verbose  Use verbose output
  -c --clock    Clock the program execution time

Available commands:
  {available_commands}

See '{program} <command> -h' for help on specific commands.
"""

main_logger = logging.getLogger("pianocktail")

@contextmanager
def precommand_config(precommand_args):
    event, stopped_event = logger_config(logging.DEBUG if precommand_args["--verbose"] else logging.INFO)
    is_clocking = precommand_args["--clock"]
    try:
        with clocking(is_clocking):
            config = load_config()
            main_logger.debug(config)
            yield config, precommand_args["--clock"]
    finally:
        sleep(1E-3)
        event.set()
        stopped_event.wait()

@contextmanager
def clocking(is_clocking):
    if is_clocking:
        main_logger.debug("Start clocking")
        start = time_ns()
        yield
        stop = time_ns()
        main_logger.info("Executed in %fs.", (stop -  start)/1E9)
    else:
        yield


@dsc.command()
def single(precommand_args, args):
    """usage: {program} single <sound>

    Analysis of a single sample.
    Used for program teakwing.

    """
    with precommand_config(precommand_args=precommand_args) as (config, is_clocking):
        main_logger.info("analyse %s", args["<sound>"])
        with clocking(is_clocking):
            clip = AudioClip( args["<sound>"], config)
            waveform = clip.sample(0)
        clip.plot_waveform(waveform, clip.metadata.sample_rate,  args["<sound>"])
        pyplot.show()
        with clocking(is_clocking):
            clip = AudioClip( args["<sound>"], config)
            spectogram = clip.spectogram(0)
        clip.plot_spectogram(spectogram, config.sampling.frequency_resolution,  args["<sound>"])
        pyplot.show()
def cli():
    dsc.main(program="pianocktail", doc_template=DOC_TEMPLATE)
