# SimpleMP

SimpleMP is a well tested, Python-first media processing API that provides a clean, reliable interface over FFmpeg through PyAV — without exposing users to the complexities of codec quirks or invalid configurations.

It focuses on deterministic behavior, strict validation, and sensible defaults to ensure media transcoding is predictable, repeatable, and easy to integrate in production.

## Why simplemp?

FFmpeg is powerful, but:

* The API surface is complex 
* PyAV exposes low-level internals directly
* Codec support is inconsistent across builds
* Invalid inputs can cause silent failures
* Filter graphs can segfault or misbehave
* Validation is basically up to the user

SimpleMP fixes this by providing a well-defined, safe, high-level API that handles:

* Input introspection
* Encoder, format and options compatibility validation
* Sample rate and bitrate safe range
* Container compatibility checks
* Error handling and reporting
* So developers can focus on using it, not debugging it.

## Features
### Simple, high-level API

```
from simplemp import transcode

transcode(
    input_file="/path/to/inputfile", output_file="/path/to/outputfile",
    audio_encoder="wmav1", video_encoder="h264",
)
```

No direct FFmpeg arguments.
No command strings.
Safe, predictable, declarative config.

## Installation

Available on PyPI:

` pip install simplemp `

Requires ` av ` and ` numpy `

## Deterministic Validation Layer

SimpleMP includes a reliable validation system that rejects invalid or unsafe configurations before encoding begins.

Validation includes:

codec ↔ container compatibility

codec ↔ sample format compatibility

codec ↔ channel count support

codec ↔ sample rate range

bitrate sanity checks

output path and directory checks

Over 400 validation tests are executed against supported formats.


## Codec Support (Audio)

Lossy:
AAC
MP3
Opus
Vorbis
Speex
WMA v1/v2

Lossless:
FLAC
ALAC
PCM (8–32 bit, be/le)
A-Law
µ-Law

## File Formats

Multi-container support:
.mp3
.m4a
.opus
.ogg
.oga
.flac
.wav
.3gp
.aif / .aifc / .aiff
.wma
.aac
.adts

## Test Suite & Quality Assurance

SimpleMP is tested like a industry grade project:

250+ test matrix entries in total
Tests for all valid codec/sample-fmt combinations
Tests for invalid combinations
Tests for failure mode correctness
Static analysis (mypy)
Unit tests + integration tests 

Example of the test matrix:

| Extension  | Codec     | Pixel Format  | Status |
|------------|-----------|---------------|--------|
| .mkv       | hevc      | yuv420p10le   |   ✔️   |
| .mkv       | hevc      | yuv422p10le   |   ✔️   |
| .mkv       | hevc      | yuv422p10le   |   ✔️   |
| .mkv       | mpeg4     | yuv420p       |   ⚠️   |
| .mkv       | vp8       | yuv420p       |   ⚠️   |
| .mkv       | vp8       | yuv422p       |   ❌   |
| .mkv       | vp8       | yuv444p       |   ❌   |

Total more than 150 tests has logged in the test matrix. 
Check ` docs/testing/TEST_MATRIX.md ` for more details.

## Author

Main api created by S.M Sadat 
and TUI is being developed by Atia Farha

## Future Plan: High-Performance C++ Edition

A C++ backend is planned using libav*, with:

templates

constexpr validation

noexcept pipelines

SIMD optimized paths

Custom filter engine

extended codec support

Estimated code size:

3,000+ LOCs validation layer
10,000+ LOCs total implementation
10,000+ LOCs for filter engine

### Python edition will remain as:
easy to use
sane defaults
fast to prototype

### C++ edition will be:
low-latency
ultra-high-performance
enterprise-ready

## Philosophy

SimpleMP is built on three principles:

* No user should need to understand codec chaos
* Invalid configs must fail instantly, not silently
* Defaults should produce production-ready results

Developer experience is a feature.


## Documentation

API usage guide: Check ` docs/api/ `
Examples: Check ` docs/examples/ `
Test matrix: Check ` docs/TEST_MATRIX.md `

## Contributing

### Contributions welcome!
#### Especially:
* test samples
* codec benchmarks
* metadata extraction
* validation logic
* CI pipelines

## License

Open source, permissive license.
To be finalized.

## Warning

API is still in it's early development phase, so expect some instability

