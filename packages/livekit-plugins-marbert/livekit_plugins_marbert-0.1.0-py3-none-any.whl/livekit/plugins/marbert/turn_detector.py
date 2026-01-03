"""
Custom Arabic EOU Turn Detector using MARBERT
"""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from livekit.agents import llm
import logging

logger = logging.getLogger("marbert-turn-detector")


class MarbertTurnDetector:
    """
    Arabic End-of-Utterance detection using fine-tuned MARBERT model.
    Compatible with LiveKit AgentSession turn_detection parameter.
    """

    def __init__(
        self,
        model_name: str = "azeddinShr/marbert-arabic-eou",
        threshold: float = 0.5,
        device: str = "cpu"
    ):
        self._model_name = model_name
        self._threshold = threshold
        self._device = device
        self._marbert_model = None
        self._tokenizer = None

        logger.info(f"Initializing MARBERT Turn Detector: {model_name}")
        self._load_model()

    def _load_model(self):
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            self._marbert_model = AutoModelForSequenceClassification.from_pretrained(
                self._model_name
            ).to(self._device)
            self._marbert_model.eval()
            logger.info(f"✓ MARBERT model loaded successfully on {self._device}")
        except Exception as e:
            logger.error(f"Failed to load MARBERT model: {e}")
            raise

    # Required properties for LiveKit
    @property
    def model(self) -> str:
        return self._model_name

    @property
    def provider(self) -> str:
        return "marbert-custom"

    async def supports_language(self, language: str | None = None) -> bool:
        if language is None:
            return True
        arabic_codes = ["ar", "ara", "ar-SA", "ar-EG", "ar-AE", "ar-MA"]
        return language in arabic_codes

    async def unlikely_threshold(self, language: str | None = None) -> float | None:
        return 0.3

    async def predict_end_of_turn(
        self,
        chat_ctx: llm.ChatContext,
        timeout: float = 3.0
    ) -> float:
        try:
            # ✅ CHANGE 1: extract ONLY the last user utterance
            text = ""
            for item in reversed(chat_ctx.items):
                if item.role == "user":
                    # Handle different content formats:
                    # - content can be a plain string
                    # - content can be a list of ChatContent (str, ChatImage, ChatAudio)
                    if isinstance(item.content, str):
                        # Content is directly a string
                        text = item.content
                    elif isinstance(item.content, list):
                        # Content is a list - extract first text element
                        for block in item.content:
                            if isinstance(block, str):
                                text = block
                                break
                    break


            if not text or not text.strip():
                logger.warning("Empty user utterance for EOU detection")
                return 0.0

            text = text.strip()

            # ✅ CHANGE 2: log the exact string sent to the model
            logger.warning(f"[EOU INPUT] >>>{repr(text)}<<<")

            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            ).to(self._device)

            with torch.no_grad():
                outputs = self._marbert_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                eou_prob = probs[0][1].item()

            logger.debug(
                f"EOU prediction for '{text[:50]}...': {eou_prob:.3f}"
            )
            return eou_prob

        except Exception as e:
            logger.error(
                f"Error during EOU prediction: {e}",
                exc_info=True
            )
            return 0.0

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float):
        if 0 <= value <= 1:
            self._threshold = value
            logger.info(f"Threshold updated to {value}")
        else:
            logger.warning(
                f"Invalid threshold {value}, must be between 0 and 1"
            )