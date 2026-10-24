from dataclasses import dataclass
from enum import StrEnum
from secrets import randbelow


class Emotion(StrEnum):
    JOY = "Freude"
    SADNESS = "Trauer"
    ANGER = "Wut"
    FEAR = "Angst"
    DISGUST = "Ekel"
    SURPRISE = "Überraschung"
    CONTEMPT = "Verachtung"


PALETTE_VERSION = "random-rgb-2.0"
LEGACY_PALETTE_VERSION = "random-rgb-1.0"
LEGACY_EMOTIONS = frozenset((*[emotion.value for emotion in Emotion], "Vertrauen"))
CURRENT_EMOTIONS = frozenset(emotion.value for emotion in Emotion)
TRIAL_COUNT = 10
ALLOWED_TRIAL_COUNTS = (10, 15)


def allowed_emotions_for_version(version: str) -> frozenset[str]:
    if version == LEGACY_PALETTE_VERSION:
        return LEGACY_EMOTIONS
    return CURRENT_EMOTIONS


@dataclass(frozen=True, slots=True)
class PaletteColor:
    id: str
    red: int
    green: int
    blue: int


def generate_random_color(color_id: str) -> PaletteColor:
    return PaletteColor(
        id=color_id,
        red=randbelow(256),
        green=randbelow(256),
        blue=randbelow(256),
    )


def generate_random_colors(count: int = TRIAL_COUNT) -> list[PaletteColor]:
    if count not in ALLOWED_TRIAL_COUNTS:
        raise ValueError("Trial count must be 10 or 15.")
    return [
        generate_random_color(f"trial-{position}") for position in range(1, count + 1)
    ]
