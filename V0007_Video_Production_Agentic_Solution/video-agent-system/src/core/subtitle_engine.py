"""Caption creation and burn-in helpers with optional transcription support."""

import re
from pathlib import Path
from typing import Any, Optional

from src.core.media_info import get_media_info
from src.core.media_utils import ensure_nonempty_output, run_ffmpeg, temporary_file, workspace_path


def _format_srt_timestamp(seconds_val: float) -> str:
    total_seconds = max(0.0, seconds_val)
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(round((total_seconds % 1) * 1000))
    if milliseconds >= 1000:
        seconds += 1
        milliseconds = 0
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def _write_transcript_srt(transcript: str, duration: float, subtitle_path: Path) -> None:
    text = transcript.strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        sentences = [text]

    segment_duration = max(0.5, duration / len(sentences))
    srt_lines = []

    for i, sentence in enumerate(sentences, start=1):
        start_t = (i - 1) * segment_duration
        end_t = min(duration, i * segment_duration)
        if i == len(sentences):
            end_t = max(end_t, duration)
        srt_lines.append(f"{i}\n{_format_srt_timestamp(start_t)} --> {_format_srt_timestamp(end_t)}\n{sentence}\n")

    subtitle_path.write_text("\n".join(srt_lines), encoding="utf-8")


def _transcribe_with_whisper(audio_path: Path) -> str:
    """Attempt automatic speech recognition using faster-whisper or whisper if installed."""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), beam_size=5)
        return " ".join(segment.text.strip() for segment in segments)
    except ImportError:
        pass

    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_path))
        return result.get("text", "").strip()
    except ImportError:
        pass

    raise RuntimeError(
        "Automatic transcription requires 'faster-whisper' or 'openai-whisper'. "
        "Provide 'transcript' text or 'subtitle_path' directly."
    )


def generate_and_burn_subtitles(
    video_path: str,
    output_path: str,
    subtitle_path: Optional[str] = None,
    transcript: Optional[str] = None,
    subtitle_output_path: Optional[str] = None,
    font_size: int = 22,
    font_color: str = "white",
) -> dict[str, Any]:
    """Burn supplied captions or transcribe audio and burn subtitles into a video."""
    video = workspace_path(video_path, must_exist=True)
    destination = workspace_path(output_path, output=True)
    info = get_media_info(str(video))
    duration = info["duration_seconds"] or 1.0

    if subtitle_path:
        captions = workspace_path(subtitle_path, must_exist=True)
    elif transcript and transcript.strip():
        if subtitle_output_path:
            captions = workspace_path(subtitle_output_path, output=True)
        else:
            captions = temporary_file("generated_captions.srt")
        _write_transcript_srt(transcript, duration, captions)
    else:
        # Attempt automatic transcription from audio
        audio_temp = temporary_file("extracted_for_transcription.wav")
        try:
            run_ffmpeg(["-i", str(video), "-vn", "-c:a", "pcm_s16le", str(audio_temp)])
            auto_transcript = _transcribe_with_whisper(audio_temp)
            if not auto_transcript:
                raise RuntimeError("Speech transcription returned empty text.")
            captions = temporary_file("auto_transcription.srt")
            _write_transcript_srt(auto_transcript, duration, captions)
        finally:
            audio_temp.unlink(missing_ok=True)

    # Windows-safe path escaping for FFmpeg subtitles filter
    raw_path = captions.as_posix()
    escaped_caption_path = raw_path.replace(":", "\\:").replace("'", "\\'")
    style_filter = f"subtitles='{escaped_caption_path}':force_style='FontSize={font_size},PrimaryColour=&H00FFFFFF,Outline=1,Shadow=1'"

    run_ffmpeg(["-i", str(video), "-vf", style_filter, "-c:a", "copy", str(destination)])
    return {
        "status": "success",
        **ensure_nonempty_output(destination),
        "subtitle_path": str(captions),
        "media_info": get_media_info(str(destination)),
    }

