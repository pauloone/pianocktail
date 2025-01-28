import logging
import os
from functools import cached_property

import torch
import torch.nn.functional as ff
import torchaudio  # type: ignore
import torchaudio.transforms  # type: ignore
from matplotlib import pyplot

from pianocktail.config import Config


class AudioClip:
    logger = logging.getLogger("audio.audio_clip.AudioClip")
    kernel_dilation = torch.Tensor([[[[1], [2], [1]]]])
    kernel_erosion = torch.Tensor([[[[1], [0], [1]]]])

    def __init__(self, name: str, config: Config, device: torch.device) -> None:
        self.logger = self.__class__.logger.getChild(f"[{name}]")
        self.config = config
        self._device = device
        self._name = name
        self._path = os.path.join(self.config.audio_location, name)
        if not os.path.isfile(self._path):
            raise ValueError(f"{self._path} is not a file")

    @cached_property
    def metadata(self) -> torchaudio.AudioMetaData:
        return torchaudio.info(self._path)

    def _time_to_frame(self, time_in_seconds: float) -> int:
        return int(self.metadata.sample_rate * time_in_seconds)

    @cached_property
    def _sample_duration_in_frame(self) -> int:
        return self._time_to_frame(self.config.sampling.duration)

    def sample(self, start: float) -> torch.Tensor:
        start_in_frame = self._time_to_frame(start)
        self.logger.debug(
            "Start: %f, duration: %f, sample_duration: %f",
            start_in_frame,
            self.metadata.num_frames,
            self._sample_duration_in_frame,
        )
        if start_in_frame + self._sample_duration_in_frame > self.metadata.num_frames:
            self.logger.error("Start duration is too late, cannot extract sample")
            raise ValueError(f"Start duration is too late: {start}, cannot extract sample")
        waveform, _ = torchaudio.load(
            self._path,
            frame_offset=start_in_frame,
            num_frames=self._sample_duration_in_frame,
        )
        waveform.to(self._device)
        if self.metadata.num_channels > 1:
            self.logger.debug("Converting to mono")
            return torch.mean(waveform, dim=0, keepdim=True)
        return waveform  # type: ignore

    @cached_property
    def freq_max(self) -> float:
        return self.metadata.sample_rate / 2  # type: ignore

    @cached_property
    def n_bins(self) -> int:
        return int(self.freq_max / self.config.sampling.frequency_resolution)

    @cached_property
    def n_fft(self) -> int:
        return int((self.n_bins - 1) * 2)

    @cached_property
    def hop_length(self) -> int:
        return self.n_fft // 2

    @cached_property
    def Spectogram_opj(self) -> torchaudio.transforms.Spectrogram:
        return torchaudio.transforms.Spectrogram(n_fft=self.n_fft, power=2)

    @cached_property
    def InverseSpectogram_opj(self) -> torchaudio.transforms.Spectrogram:
        return torchaudio.transforms.GriffinLim(n_fft=self.n_fft)

    def spectogram(self, start: float) -> torch.Tensor:
        return self.Spectogram_opj(self.sample(start))[0, :, :]  # type: ignore

    def filtered_spectogram(self, start: float) -> torch.Tensor:
        spectogram = self.spectogram(start)
        d_spectogram = ff.conv2d(
            spectogram.reshape(1, 1, *spectogram.shape),
            self.kernel_erosion,
            padding="same",
        )
        return ff.conv2d(d_spectogram, self.kernel_dilation, padding="same")[0, 0, :, :]

    def _frequency_to_bin(self, frequency: float) -> int:
        return int(frequency // self.config.sampling.frequency_resolution)

    def peaks(self, start: float) -> torch.Tensor:
        spectogram = self.filtered_spectogram(start)
        bins = [self._frequency_to_bin(f) for f in self.config.sampling.frequency_range]

        return spectogram

    def plot_waveform(self, waveform: torch.Tensor, prefix: str = "Waveform") -> None:
        t_axis = torch.arange(0, waveform.shape[1]) / self.metadata.sample_rate
        figure, axes = pyplot.subplots()
        axes.plot(t_axis, waveform[0], linewidth=1)

        figure.suptitle(f"{prefix}: {self._name}")

    def plot_spectogram(self, spectogram: torch.Tensor, name: str = "spectogram") -> None:
        spectogram = 20 * torch.log10(spectogram + 1e-12)
        figure, axes = pyplot.subplots()
        freq_size, time_size = spectogram.shape
        self.logger.debug("freq_size %f, time_size: %f", freq_size, time_size)
        duration = time_size / (self.metadata.sample_rate / self.hop_length)
        axes.imshow(
            spectogram,
            cmap="viridis",
            origin="lower",
            aspect="auto",
            extent=(0, duration, 0, self.freq_max),
        )
        figure.suptitle(name)

    def write_spectogram_to_audio(self, spectogram: torch.Tensor, filename: str) -> None:
        waveform = self.InverseSpectogram_opj(spectogram)
        torchaudio.save(filename, waveform.reshape(1, *waveform.shape), self.metadata.sample_rate)
