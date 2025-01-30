import logging
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from time import sleep, time_ns

import docopt_subcommands as dsc  # type: ignore
import torch
import torch.cuda
from matplotlib import pyplot
from peewee import SqliteDatabase
from peewee_migrate import Router

from .audio.audio_clip import AudioClip
from .config import Config, load_config
from .dataset import models
from .utils.logging import logger_config

DOC_TEMPLATE = """{program}

Usage: {program} [options] <command> [<args> ...]

Options:
  -h --help     Show this screen.
  -v --verbose  Use verbose output
  -c --clock    Clock the program execution time
  --no-cuda     Deactivate cuda
  --database_path=<path>  Path to the database [default: pianocktail.db]

Available commands:
  {available_commands}

See '{program} <command> -h' for help on specific commands.
"""

main_logger = logging.getLogger("pianocktail")


@dataclass(frozen=True)
class Precommand:
    config: Config
    clocking: bool
    device: torch.device
    database: SqliteDatabase


@contextmanager
def precommand_config(
    precommand_args: typing.Dict[str, typing.Any],
) -> typing.Generator[Precommand, None, None]:
    event, stopped_event = logger_config(logging.DEBUG if precommand_args["--verbose"] else logging.INFO)
    is_clocking = precommand_args["--clock"]
    database = SqliteDatabase(precommand_args["--database_path"])
    models.set_database(database)
    if torch.cuda.is_available() and not precommand_args["--no-cuda"]:
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    try:
        with clocking(is_clocking):
            config = load_config()
            main_logger.debug(config)
            yield Precommand(config, precommand_args["--clock"], device, database)
    finally:
        sleep(1e-3)
        event.set()
        stopped_event.wait()


@contextmanager
def clocking(is_clocking: bool) -> typing.Generator[None, None, None]:
    if is_clocking:
        main_logger.debug("Start clocking")
        start = time_ns()
        yield
        stop = time_ns()
        main_logger.info("Executed in %fs.", (stop - start) / 1e9)
    else:
        yield


@dsc.command()  # type: ignore
def single(precommand_args: dict[str, typing.Any], args: dict[str, typing.Any]) -> None:
    """usage: {program} single <sound> [--display]

    Analysis of a single sample.
    Used for program teakwing.

    """
    with precommand_config(precommand_args=precommand_args) as precommand:
        main_logger.info("Extracting sample")
        with clocking(precommand.clocking):
            clip = AudioClip(args["<sound>"], precommand.config, precommand.device)
            waveform = clip.sample(0)

        main_logger.info("Extracting spectrogram")
        with clocking(precommand.clocking):
            spectogram = clip.spectogram(0)

        main_logger.info("Filter spectrogram")
        with clocking(precommand.clocking):
            filtered_spectogram = clip.filtered_spectogram(0)

        main_logger.info("Get peaks")
        with clocking(precommand.clocking):
            peaks = clip.peaks(0)
        p_spectogram = clip.peaks_to_spectogram(peaks, spectogram.shape)

        clip.write_spectogram_to_audio(spectogram, f"raw_{args['<sound>']}")
        clip.write_spectogram_to_audio(filtered_spectogram, f"filtered_{args['<sound>']}")
        clip.write_spectogram_to_audio(p_spectogram, f"peak_{args['<sound>']}")

        if args["--display"]:

            clip.plot_waveform(waveform, "Raw waveform")
            clip.plot_spectogram(spectogram, "Raw spectogram")
            clip.plot_spectogram(filtered_spectogram, "Filtered spectogram")
            clip.plot_spectogram(p_spectogram, "peaks")
            pyplot.show()


@dsc.command()  # type: ignore
def process_raw_dataset(precommand_args: dict[str, typing.Any], args: dict[str, typing.Any]) -> None:
    """usage: {program} raw_dataset [--path=<path>]

    Process the raw dataset configuration.


    """
    with precommand_config(precommand_args=precommand_args):
        main_logger.info("Nothing for now")


@dsc.command()  # type: ignore
def process_database(precommand_args: dict[str, typing.Any], args: dict[str, typing.Any]) -> None:
    """usage:
        {program} database generate_migration
        {program} database migrate [<migration>]

    Manage the dataset database.


    """
    with precommand_config(precommand_args=precommand_args) as precommand:
        router = Router(precommand.database, migrate_dir=f"{models.__path__[0]}/migrations")
        if args["generate_migration"]:
            router.create(auto=True)
        if args["migrate"]:
            router.run(args.get("<migration>"))


def cli() -> None:
    dsc.main(program="pianocktail", doc_template=DOC_TEMPLATE)
