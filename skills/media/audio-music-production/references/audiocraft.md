# AudioCraft — Meta's MusicGen & AudioGen

AudioCraft is Meta's open-source framework for audio generation. Two main models:

| Model | Purpose | Sizes |
|-------|---------|-------|
| **MusicGen** | Text-to-music generation | small (300M), medium (1.5B), large (3.3B) |
| **AudioGen** | Text-to-sound effects | medium (1.5B) |

## Quick Start

```bash
pip install audiocraft
```

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=8)

wav = model.generate(["upbeat electronic dance music with synths"])
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

## HuggingFace Transformers

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
model.to("cuda")

inputs = processor(text=["80s pop track with bassy drums"], padding=True, return_tensors="pt").to("cuda")
audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=256)
sampling_rate = model.config.audio_encoder.sampling_rate
scipy.io.wavfile.write("output.wav", rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
```

## Melody Conditioning

```python
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)
melody, sr = torchaudio.load("melody.wav")
wav = model.generate_with_chroma(["acoustic guitar folk song"], melody, sr)
```

## Text-to-Sound (AudioGen)

```python
from audiocraft.models import AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')
model.set_generation_params(duration=5)
wav = model.generate(["dog barking in a park with birds chirping"])
torchaudio.save("sound.wav", wav[0].cpu(), sample_rate=16000)
```

## GPU Memory Requirements

| Model | FP32 VRAM | FP16 VRAM |
|-------|-----------|-----------|
| musicgen-small | ~4GB | ~2GB |
| musicgen-medium | ~8GB | ~4GB |
| musicgen-large | ~16GB | ~8GB |

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | 8.0 | Length in seconds (1-120) |
| `top_k` | 250 | Top-k sampling |
| `temperature` | 1.0 | Sampling temperature |
| `cfg_coef` | 3.0 | Classifier-free guidance |

## Pitfalls

- CUDA OOM → use smaller model, reduce duration
- Poor quality → increase cfg_coef, use better prompts
- Stereo → use `musicgen-stereo-medium` variant
- Audio artifacts → try different temperature

## Resources

- GitHub: https://github.com/facebookresearch/audiocraft
- Paper (MusicGen): https://arxiv.org/abs/2306.05284
- Paper (AudioGen): https://arxiv.org/abs/2209.15352