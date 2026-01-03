# LiveKit MARBERT Turn Detector

Arabic End-of-Utterance detection plugin for LiveKit Agents using fine-tuned MARBERT.

## Installation
```bash
pip install livekit-plugins-marbert
```

Or install from source:
```bash
pip install git+https://github.com/azeddinshr/livekit-plugins-marbert.git
```

## Quick Start
```python
from livekit.plugins.marbert import MarbertTurnDetector
from livekit.agents import Agent, AgentSession, JobContext, JobProcess, WorkerOptions, cli
from livekit.plugins import openai, silero

def prewarm(proc: JobProcess):
    """Load models once at startup (recommended for production)."""
    proc.userdata["vad"] = silero.VAD.load()
    proc.userdata["marbert"] = MarbertTurnDetector(
        model_name="azeddinShr/marbert-arabic-eou",
        device="cpu"
    )

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession(
        stt=openai.STT(model="gpt-4o-transcribe", language="ar"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(model="gpt-4o-mini-tts"),
        vad=ctx.proc.userdata["vad"],
        turn_detection=ctx.proc.userdata["marbert"]
    )
    
    agent = Agent(instructions="أنت مساعد سعودي ذكي")
    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
```

See [examples/basic_usage.py](examples/basic_usage.py) for a complete working example.

## Features

- ✅ Fine-tuned on 125K Arabic utterances (SADA22 dataset)
- ✅ Specialized for Saudi dialect
- ✅ 77% F1 score, 30ms average CPU latency
- ✅ Drop-in replacement for LiveKit turn detector
- ✅ Compatible with LiveKit Agents 1.3.9+
- ✅ Production-ready with prewarm support

## Performance

| Metric | MARBERT | LiveKit Multilingual |
|--------|---------|---------------------|
| **F1 Score** | 0.77 | 0.66* |
| **Latency (CPU)** | 30ms | 300ms* |
| **Language** | Arabic (Saudi) | 14 languages |
| **Model Size** | 163M params | 500M params |

*Comparison with community Arabic model

## Model Details

- **Base Model:** [UBC-NLP/MARBERT](https://huggingface.co/UBC-NLP/MARBERT) (163M parameters)
- **Fine-tuned Model:** [azeddinShr/marbert-arabic-eou](https://huggingface.co/azeddinShr/marbert-arabic-eou)
- **Training Dataset:** [azeddinShr/arabic-eou-sada22](https://huggingface.co/datasets/azeddinShr/arabic-eou-sada22)
- **Task:** Binary classification (complete vs incomplete utterance)
- **Training Data:** 125K samples from SADA22 (Saudi dialect focus)

## Configuration
```python
MarbertTurnDetector(
    model_name="azeddinShr/marbert-arabic-eou",  # HuggingFace model ID
    threshold=0.5,                                 # EOU probability threshold
    device="cpu"                                   # "cpu" or "cuda"
)
```

## Requirements

- Python >= 3.9
- livekit-agents >= 1.3.9
- transformers >= 4.30.0
- torch >= 2.0.0

## License

Apache 2.0

## Citation

If you use this model in your research, please cite:
```bibtex
@misc{marbert-arabic-eou,
  author = {Sahir, Azeddin},
  title = {MARBERT Arabic End-of-Utterance Detection},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/azeddinshr/livekit-plugins-marbert}
}
```

## Links

- [GitHub Repository](https://github.com/azeddinshr/livekit-plugins-marbert)
- [Fine-tuned Model](https://huggingface.co/azeddinShr/marbert-arabic-eou)
- [Training Dataset](https://huggingface.co/datasets/azeddinShr/arabic-eou-sada22)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)