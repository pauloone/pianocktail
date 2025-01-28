import logging
import typing
from contextlib import contextmanager
from time import sleep, time_ns

import docopt_subcommands as dsc  # type: ignore
import torch
import torch.cuda
from matplotlib import pyplot

from .audio.audio_clip import AudioClip
from .config import Config, load_config
from .utils.logging import logger_config

DOC_TEMPLATE = """{program}

Usage: {program} [options] <command> [<args> ...]

Options:
  -h --help     Show this screen.
  -v --verbose  Use verbose output
  -c --clock    Clock the program execution time
  --no-cuda     Deactivate cuda

Available commands:
  {available_commands}

See '{program} <command> -h' for help on specific commands.
"""

main_logger = logging.getLogger("pianocktail")


@contextmanager
def precommand_config(
    precommand_args: typing.Dict[str, typing.Any],
) -> typing.Generator[tuple[Config, bool, torch.device], None, None]:
    event, stopped_event = logger_config(logging.DEBUG if precommand_args["--verbose"] else logging.INFO)
    is_clocking = precommand_args["--clock"]
    if torch.cuda.is_available() and not precommand_args["--no-cuda"]:
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    try:
        with clocking(is_clocking):
            config = load_config()
            main_logger.debug(config)
            yield config, precommand_args["--clock"], device
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
    with precommand_config(precommand_args=precommand_args) as (
        config,
        is_clocking,
        torch_device,
    ):
        main_logger.info("Extracting sample")
        with clocking(is_clocking):
            clip = AudioClip(args["<sound>"], config, torch_device)
            waveform = clip.sample(0)

        main_logger.info("Extracting spectrogram")
        with clocking(is_clocking):
            spectogram = clip.spectogram(0)

        main_logger.info("Filter spectrogram")
        with clocking(is_clocking):
            filtered_spectogram = clip.filtered_spectogram(0)

        main_logger.info("Get peaks")
        with clocking(is_clocking):
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


def cli() -> None:
    dsc.main(program="pianocktail", doc_template=DOC_TEMPLATE)
