
import logging
import torchaudio
import torchaudio.transforms
import torch
import os
from pianocktail.config import Config
from functools import cached_property
from matplotlib import pyplot

class AudioClip:
    logger = logging.getLogger("audio.audio_clip.AudioClip")
    __config = None
    def __init__(self, name: str, config: Config) -> None:
        self.logger = self.__class__.logger.getChild(f"[{name}]")
        self.config = config
        self._path = os.path.join(self.config.audio_location, name)
        if not os.path.isfile(self._path):
            raise ValueError(f"{self._path} is not a file")

    @cached_property
    def metadata(self):
        return torchaudio.info(self._path)
    
    def _time_to_frame(self, time_in_seconds: float) -> int:
        return int(self.metadata.sample_rate * time_in_seconds)
    
    @cached_property
    def _sample_duration_in_frame(self) -> int:
        return self._time_to_frame(self.config.sampling.duration)
    

    def sample(self, start: float) -> torch.Tensor:
        start_in_frame = self._time_to_frame(start)
        self.logger.debug("Start: %f, duration: %f, sample_duration: %f", start_in_frame, self.metadata.num_frames, self._sample_duration_in_frame)
        if start_in_frame + self._sample_duration_in_frame > self.metadata.num_frames:
            self.logger.error("Start duration is too late, cannot extract sample"
                              )
            raise ValueError(f"Start duration is too late: {start}, cannot extract sample")
        waveform, sample_rate =  torchaudio.load(self._path, frame_offset=start_in_frame, num_frames=self._sample_duration_in_frame)
        if self.metadata.num_channels > 1:
            self.logger.debug("Converting to mono")
            return torch.mean(waveform, dim = 0, keepdim=True)

    @cached_property
    def Spectogram_opj(self) -> torchaudio.transforms.Spectrogram:
        freq_max = self.metadata.sample_rate /2
        n_bins = freq_max/self.config.sampling.frequency_resolution
        n_fft = int((n_bins - 1) * 2)
        self.logger.debug("Nbins: %f", n_bins)
        return torchaudio.transforms.Spectrogram(n_fft=n_fft)

    def spectogram(self, start: float) -> tuple[torch.Tensor, int]:
        return self.Spectogram_opj(self.sample(start))
        
    @classmethod
    def plot_waveform(cls, waveform: torch.Tensor, sample_rate: int, name: str = "waveform") -> None:
        waveform = waveform.numpy()
        t_axis = torch.arange(0, waveform.shape[1]) / sample_rate
        figure, axes = pyplot.subplots()
        axes.plot(t_axis, waveform[0], linewidth=1)

        figure.suptitle(f"Waveform: {name}")

    @classmethod
    def plot_spectogram(cls, spectogram: torch.Tensor, frequency_resolution: float, name: str = "waveform") -> None:
        spectogram = 20 * torch.log10(spectogram + 1E-12)[0,:,:].numpy()
        figure, axes = pyplot.subplots()
        freq_size, time_size = spectogram.shape
        cls.logger.debug("freq_size %f, time_size: %f", freq_size, time_size)
        freq_max = freq_size * frequency_resolution
        n_bins = freq_max/frequency_resolution
        n_fft = int((n_bins - 1) * 2)
        hop_length = n_fft // 2
        sample_rate = freq_max * 2
        duration = time_size/ (sample_rate / hop_length)
        cls.logger.debug("n_fft %f", n_fft)
        cls.logger.debug("hop_length %f", hop_length)
        cls.logger.debug("freq_max %f, time_max: %f", freq_max, duration)
        axes.imshow(spectogram, cmap="viridis", origin="lower", aspect="auto", extent=[0, duration, 0, freq_max])
        figure.suptitle(f"Spectogram: {name}")


    