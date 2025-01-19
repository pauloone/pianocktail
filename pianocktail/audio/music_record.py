# Define a music record
from io import BytesIO
from numpy import array
from scipy.io import wavfile
from functools import lru_cache, cached_property

class MusicRecord():

    def ___init__(self, wav_path: str | BytesIO):

        self._sample_rate, self._data, wavfile(wav_path)
    
    def sample_rate(self) -> int:
        return self._sample_rate
    
    def data(self) -> int:
        return self._data