---
name: audio-music-production
description: "Umbrella for music and audio creation: songwriting craft, Suno/AI music prompting, open-source music generation (HeartMuLa), and audio spectrogram/feature visualization (songsee)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [music, audio, songwriting, suno, heartmula, spectrogram, music-generation, audio-analysis, lyrics]
    related_skills: []
---

# Audio & Music Production

Three complementary domains for working with music and audio through AI:

| Domain | Skill | When to Use |
|--------|-------|-------------|
| **Songwriting §1** | Lyric craft, song structure, rhyme/meter | User wants to write original lyrics, parodies, or adapt an existing song |
| **Suno AI Prompting §2** | Style descriptions, metatags, phonetic tricks | User wants to generate music via Suno AI with custom lyrics |
| **Music Generation §3** | HeartMuLa open-source model | User wants local/offline music generation from lyrics + tags |
| **Audio Visualization §4** | songsee spectrograms/features | User wants to visualize audio files, debug synthesis, compare outputs |

---

## §1 Songwriting Craft

### Song Structure (Pick One or Invent Your Own)

```
ABABCB  Verse/Chorus/Verse/Chorus/Bridge/Chorus    (most pop/rock)
AABA    Verse/Verse/Bridge/Verse (refrain-based)    (jazz standards, ballads)
ABAB    Verse/Chorus alternating                    (simple, direct)
AAA     Verse/Verse/Verse (strophic, no chorus)     (folk, storytelling)
```

Building blocks: Intro → Verse → Pre-Chorus → Chorus → Bridge → Outro.

### Rhyme, Meter, and Sound

**Rhyme types** (from tight to loose): Perfect (lean/mean) → Family (crate/braid) → Assonance (had/glass) → Consonance (scene/when) → Near/slant.

**Internal Rhyme:** Rhyming within a line, not just at the ends.

**Meter:** The rhythm of stressed vs unstressed syllables. Matching syllable counts between parallel lines helps singability.

### Emotional Arc and Dynamics

Think of a song as a journey: Whisper before a scream hits harder. Sparse before dense. Slow before fast. Silence is an instrument.

### Parody and Adaptation

When rewriting an existing song:
1. Map original structure (syllables, rhyme, stress)
2. Match stressed syllables to original beats
3. Total syllable count can flex by 1-2 unstressed syllables
4. On long held notes, match the VOWEL SOUND of the original
5. Sing new words over the original — revise if it stumbles

### Key Rules

- Show, don't tell (usually)
- Avoid cliches on autopilot
- Don't force word order to hit a rhyme ("Yoda-speak")
- Revision is creation

---

## §2 Suno AI Prompt Engineering

### Style/Genre Description Formula

```
Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics
```

Describe the JOURNEY, not just the genre:
```
"Begins as a haunting whisper over sparse piano. Gradually layers in muted brass. Builds through the chorus. Second verse erupts. Outro strips back to a lone piano."
```

### Metatags (place in [brackets] inside lyrics field)

Structure: `[Intro] [Verse] [Pre-Chorus] [Chorus] [Bridge] [Outro] [Instrumental]`
Vocal: `[Whispered] [Spoken Word] [Belted] [Falsetto] [Powerful] [Soulful] [Raspy]`
Dynamics: `[High Energy] [Low Energy] [Building Energy] [Explosive] [Emotional Climax]`
Atmosphere: `[Melancholic] [Euphoric] [Nostalgic] [Aggressive] [Dreamy]`

### Phonetic Tricks for AI Singers

- Spell words as they sound: "through" → "thru", "Nous" → "Noose"
- ALL CAPS = louder, more intense
- Vowel extension: "lo-o-o-ove" = sustained/melisma
- Spell out numbers: "24/7" → "twenty four seven"
- Space acronyms: "AI" → "A I" or "A-I"

### Workflow

1. Write concept/hook first
2. Generate raw material
3. Draft lyrics into structure
4. Read aloud — catch stumbles
5. Build Suno style description
6. Add metatags
7. Generate 3-5 variations minimum
8. Use Extend/Continue to build on promising sections
9. ~3-5 generations per 1 good result — revision is normal

---

## §3 HeartMuLa — Open-Source Music Generation

Generate songs from lyrics + tags using Apache-2.0 open-source models. Comparable to Suno.

### Hardware Requirements

| Setup | VRAM |
|-------|------|
| Minimum | 8GB VRAM (with `--lazy_load true`) |
| Recommended | 16GB+ VRAM |
| Multi-GPU | Split via `--mula_device cuda:0 --codec_device cuda:1` |
| No GPU | CPU mode works but extremely slow (~30-60 min per song) |

### Installation

```bash
git clone https://github.com/HeartMuLa/heartlib.git ~/heartlib
cd ~/heartlib
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
# Fix dependency conflicts:
uv pip install --upgrade datasets transformers
```

### Patch Required for transformers 5.x

See `references/heartmula-patches.md` for the two required source code patches.

### Usage

```bash
cd ~/heartlib && . .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length (240s = 4 min) |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temperature |
| `--cfg_scale` | 1.5 | Classifier-free guidance scale |
| `--lazy_load` | false | Load/unload models on demand |

### Tag Format

```
piano,happy,wedding,synthesizer,romantic
```

### Lyrics Format (bracketed structural tags)

```
[Intro]
[Verse]
Your lyrics here...
[Chorus]
Chorus lyrics...
[Bridge]
[Outro]
```

### Pitfalls

- Do NOT use bf16 for HeartCodec — degrades quality. Use fp32.
- Tags may be ignored (known issue #90) — lyrics dominate
- Triton not available on macOS
- RTX 5080 incompatibility reported

---

## §4 Audio Visualization (songsee)

Generate spectrograms and multi-panel audio feature visualizations.

### Installation

```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

### Quick Start

```bash
songsee track.mp3 -o spectrogram.png
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg
```

### Visualization Types

| Type | Description |
|------|-------------|
| `spectrogram` | Standard frequency spectrogram |
| `mel` | Mel-scaled spectrogram |
| `chroma` | Pitch class distribution |
| `hpss` | Harmonic/percussive separation |
| `selfsim` | Self-similarity matrix |
| `loudness` | Loudness over time |
| `tempogram` | Tempo estimation |
| `mfcc` | Mel-frequency cepstral coefficients |
| `flux` | Spectral flux (onset detection) |

### Common Flags

| Flag | Description |
|------|-------------|
| `--style` | Color palette: `classic`, `magma`, `inferno`, `viridis`, `gray` |
| `--width` / `--height` | Output image dimensions |
| `--window` / `--hop` | FFT window and hop size |
| `--min-freq` / `--max-freq` | Frequency range |
| `--start` / `--duration` | Time slice |

### Notes

- WAV and MP3 decoded natively; other formats need `ffmpeg`
- Output images can be inspected with `vision_analyze` for automated audio analysis

---

## References

- `references/heartmula-patches.md` — Required source patches for HeartMuLa + transformers 5.x compatibility