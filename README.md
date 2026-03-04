# toolconv

`toolconv` is the GitHub project name for **Borstbindare Wenman**, an offline-first media conversion tool for desktop operating systems.

The long-term goal is a cross-platform converter for macOS (Intel and Apple Silicon), Windows, and Linux. The first implemented conversion is:

- `MP4 -> WAV`

The project is intentionally structured so more conversions can be added later without rewriting the core.

## Why this exists

- Runs locally and works offline
- Uses `ffmpeg`, which is mature and cross-platform
- Keeps the first version small and reliable
- Can grow into more file-to-file conversions over time

## Requirements

- [Node.js](https://nodejs.org/) 18+ recommended
- `ffmpeg` installed and available in your `PATH`

## Install locally

From the project folder:

```bash
npm install
```

No external npm dependencies are used in this version, so install is mainly for creating the CLI link if you package or publish it later.

## Usage

### Start the local UI

```bash
node ./bin/toolconv.js serve
```

Then open:

```text
http://127.0.0.1:3000
```

You can choose a different port:

```bash
node ./bin/toolconv.js serve --port 4321
```

### CLI usage

```bash
node ./bin/toolconv.js convert input.mp4 output.wav
```

Or, after linking/installing the package as a CLI:

```bash
toolconv convert input.mp4 output.wav
```

You can also use the branded alias:

```bash
borstbindare-wenman convert input.mp4 output.wav
```

## Current support

- `mp4 -> wav`: extracts the audio track from an MP4 file and writes a WAV file (`pcm_s16le`)
- Local web UI for `MP4 -> WAV`, running fully on your own machine

## Project direction

Planned future additions can include:

- More audio conversions (`mp3 -> wav`, `wav -> mp3`)
- More video conversions (`mov -> mp4`)
- Cross-type exports (`mp4 -> wav`)
- Image conversions where the underlying toolchain can support them cleanly
- A packaged standalone release workflow per platform
- A desktop wrapper so the UI can launch like a native app

## License

MIT
