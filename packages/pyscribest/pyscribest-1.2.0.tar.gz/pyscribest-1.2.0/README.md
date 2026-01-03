# :musical_note: ***Pyscribe***
A robust tool to transcribe audio (including music) files and URLs using **ElevenLabs Scribe** AI model.

## :clipboard: Requirements
- 64-bit operating system
- Python 3.8+ if not using standalone binary
- ElevenLabs API key ([instructions](#zap-usage) below)

## :rocket: Installation
### Prebuilt standalone binary (Windows, macOS, Linux)
Download a standalone binary from
[the latest release](https://github.com/tooruu/pyscribe/releases/latest). Comes with keyring support.

### Install from PyPI
If you don't want to enter your API key every time, the optional `keyring` dependency allows
***Pyscribe*** to securely store it in your system's credential store.
```bash
# Recommended: Installation with keyring support
pip install "pyscribest[keyring]"
# Minimal installation without keyring support
pip install pyscribest
```

### Run the tool without installation using uv[^1]
```bash
# With keyring support
uvx "pyscribest[keyring]" "path/or/url.mp3"
# Without keyring support
uvx pyscribest "path/or/url.mp3"
```
###### pyscribe was taken [🥹](https://discord.gg/YdEXsZN)

## :zap: Usage
> [!IMPORTANT]
> ### API Key Configuration
> Log in to your [ElevenLabs dashboard](https://elevenlabs.io/app/developers/api-keys)
> and create an API key with access to **Speech to Text** endpoint.
>
> The script looks for the API key in the following order:
> 1. **Environment Variable**: Looks for the `ELEVENLABS_API_KEY` environment variable.
> 2. **System Credential Store**: Automatically saved to by the other methods if `keyring` is installed.
> 3. **Terminal Prompt**: If terminal is detected, prompt user for the key without displaying it.
> 4. **Standard Input**: Read one line from `sys.stdin`.

### Basic Transcription
```bash
pyscribe "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
```

In the spirit of Unix philosophy only successful transcription prints to `sys.stdout`.
Everything else is written to `sys.stderr`.\
Use your shell's **output redirection operator** to write transcription to disk.

```bash
pyscribe "Never Gonna Give You Up.webm" > lyrics.txt
```

> [!NOTE]
> `python -m pyscribe` is available as an alternative if installed via `pip`.
>
> The `pyscribest` entrypoint is intended to avoid typing `uvx --from pyscribest pyscribe`.

### CLI Options
- `--full`: Insert audio event tags like `[laughter]`.
- `--lang`: An [ISO-639-1](https://www.loc.gov/standards/iso639-2/php/English_list.php) or
  [ISO-639-3](https://iso639-3.sil.org/code_tables) language code[^2] for improved performance,
  e.g. `de` or `deu` for German.
- `--no-keyring`: Avoid reading or writing key to the system keyring.
- `-v`, `--verbose`: Show diagnostic messages.
- `-V`, `--version`: Print program's version and exit.

```bash
pyscribe --lang deu --full recording.wav -v
```

## :hammer_and_wrench: Integration
The `pyscribe` package provides both synchronous and asynchronous
interfaces for seamless integration into any project.

### Sync
```py
from elevenlabs import ElevenLabs
from pyscribe import transcribe

client = ElevenLabs(api_key="YOUR API KEY")
text = transcribe(client, "path/or/url.mp3")
print(text)
```

### Async
```py
from elevenlabs import AsyncElevenLabs
from pyscribe import atranscribe

client = AsyncElevenLabs(api_key="YOUR API KEY")
text = await atranscribe(client, "path/or/url.mp3")
print(text)
```

> [!TIP]
> The `elevenlabs` SDK is included as a dependency; no separate installation is required.

## :stop_sign: API Limitations
### Concurrency
ElevenLabs imposes [limitations](https://elevenlabs.io/docs/overview/models#concurrency-and-priority)
on concurrent **Speech to Text** requests.\
For example, the free plan only allows 8 transcription requests at the same time.

### File Size
ElevenLabs also imposes different file size limits:
- **Local files** &mdash; up to 3 GB[^3]
- **Remote HTTPS files** &mdash; up to 2 GB[^4]

### Features
***Pyscribe*** focuses on end users and aims to provide a simple interface for the **Scribe** model.\
As such, this tool does not implement all **Scribe** features, including but not limited to:
- Webhook support
- Word-level timestamps
- Speaker diarization
- Output in other formats

[^1]: [Documentation for `uvx`](https://docs.astral.sh/uv/guides/tools)
[^2]: [Supported Languages](https://elevenlabs.io/docs/overview/capabilities/speech-to-text#supported-languages)
[^3]: [`file` Parameter Description](https://elevenlabs.io/docs/api-reference/speech-to-text/convert#request.body.file.file)
[^4]: [`cloud_storage_url` Parameter Description](https://elevenlabs.io/docs/api-reference/speech-to-text/convert#request.body.cloud_storage_url.cloud_storage_url)
