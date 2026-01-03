"""
LiveKit MARBERT Turn Detector Plugin
Arabic End-of-Utterance detection using fine-tuned MARBERT
"""

from .turn_detector import MarbertTurnDetector
from .version import __version__

__all__ = ["MarbertTurnDetector", "__version__"]