from simplemp import transcode
from simplemp.logs import get_terminal_logs

transcode(
    input_file="../dump/testv0.0.7/stay.mp4", output_file="../dump/testv0.0.7/stay2.mkv",
    audio_encoder="pcm_s16le", samplerate=11025, bitrate_audio=32000, sample_fmt="s16",
    video_encoder="h264", bitrate_video=9000000, pixel_fmt="yuv420p", frame_rate=60, 
    crf=24, preset="slow", profile="baseline", tune="zerolatency",
    resolution=(1920, 1080),
    mute=False, debug=True, overwrite=False, thread_count=3, thread_type="SLICE", loop=3
)

