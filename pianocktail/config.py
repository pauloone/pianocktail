from dataclasses import dataclass
import yaml


@dataclass(frozen=True)
class SamplingConfig:
    duration: float
    frequency_resolution: float


@dataclass(frozen=True)
class Config:
    audio_location: str
    sampling: SamplingConfig


def load_config(path: str = "pianocktail.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        data["sampling"] = SamplingConfig(**data["sampling"])

        return Config(**data)
