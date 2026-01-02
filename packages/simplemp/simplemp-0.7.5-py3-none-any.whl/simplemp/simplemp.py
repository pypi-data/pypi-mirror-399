import os
from typeguard import typechecked

import av
import av.logging

from .validator import check_media_compat
from .simplempcore import smpcore

@typechecked
def transcode(
    
    input_file: str = "",
    output_file: str = "",
    overwrite: bool = False,        
    debug: bool = False,            
    thread_count: int = 0,        
    thread_type: str = "AUTO",       
    mute: bool = False,             
    loop: int = 1,                  

    audio_encoder: str = "",          
    samplerate: int = 44100,        
    sample_fmt: str = "",          
    bitrate_audio: int = 192000,         

    video_encoder: str = "",          
    pixel_fmt: str = "",            
    bitrate_video: int = 192000,     
    resolution = (int, int),        
    frame_rate: int = 30,                                   
    crf: int = 24,                  
    preset: str = "fast",          
    profile : str = "high", 
    tune : str = "zerolatency",
):
    """
    Transcode audio and/or video media files using FFmpeg.

    This function serves as the main frontend for **SimppleMP** and supports
    flexible audio and video transcoding with configurable codecs, formats,
    and quality parameters.

    Parameters are grouped in 3 categories

    ---------------------------------------------------------------------------------
    1. General
    
    input_file : str
        Path to the input media file.

    output_file : str
        Path to the output media file.

    overwrite : bool, optional
        Whether to overwrite the output file if it already exists.
        Default is ``False``.

    debug : bool, optional
        Enable verbose debug output.
        Default is ``False``.

    thread_count : int, optional
        Number of FFmpeg threads to use.
        ``0`` means automatic thread selection.
        Default is ``0``.

    thread_type : strm optional
        Types of threading to use,
        Default is ``AUTO``
        Available options: ``AUTO`` ``FRAME`` ``SLICE``

    mute : bool, optional
        Remove the audio stream from the output.
        Default is ``False``.

    loop : int, optional
        Number of times to loop the input media.
        ``0`` means no looping.
        Default is ``0``.

    ---------------------------------------------------------------------------------
    2. Audio

    codec_audio : str, optional
        Audio codec to use for transcoding (e.g. ``aac``, ``mp3``, ``pcm_s16le``).
        If empty, FFmpeg chooses a default codec.

    samplerate : int, optional
        Audio sample rate in Hz.
        Default is ``44100``.

    sample_fmt : str, optional
        Audio sample format (e.g. ``pcm_s16le``, ``pcm_f32le``).
        If empty, FFmpeg chooses a default format.

    bitrate_audio : int, optional
        Audio bitrate in bits per second for compressed formats.
        Default is ``192000`` (192 kbps).

    ---------------------------------------------------------------------------------
    3. Video

    codec_video : str, optional
        Video codec to use for transcoding (e.g. ``libx264``, ``libx265``).
        If empty, FFmpeg chooses a default codec.

    pixel_fmt : str, optional
        Video pixel format (e.g. ``yuv420p``, ``rgb24``).
        If empty, FFmpeg chooses a default format.

    bitrate_video : int, optional
        Video bitrate in bits per second.
        Default is ``192000``.

    resolution : tuple(int, int)
        Output video resolution as ``(width, height)``.
        Common values include:
        ``1920x1080``, ``1280x720``, ``854x480``,
        ``640x480``, ``640x360``, ``320x240``.

    frame_rate : int, optional
        Output video frame rate (frames per second).
        Default is ``30``.

    crf : int, optional
        Constant Rate Factor for quality-based encoding.
        Lower values produce higher quality and larger files.
        Default is ``24``.

    preset : str, optional
        Encoder preset controlling speed vs compression efficiency
        (e.g. ``ultrafast``, ``fast``, ``medium``, ``slow``).
        Default is ``"fast"``.

    profile : str, optional
        Video encoding profile (e.g. ``baseline``, ``main``, ``high``).
        Default is ``"high"``.

    tune : str, optional
        Encoder tuning option (e.g. ``zerolatency``, ``film``, ``animation``).
        Default is ``"zerolatency"``.

    Returns
    -------
    None
        This function performs transcoding as a side effect and does not
        return a value.

    Raises
    ------
    ValueError
        If invalid or incompatible parameter values are provided.

    RuntimeError
        If FFmpeg fails during the transcoding process.
    """

    if debug: 
        av.logging.set_level(av.logging.DEBUG)

    # ===== check file existence

    if not input_file or not os.path.exists(input_file): 
        print("SimpleMP: Input file doesn't exist")
        return

    # Output file unneccessary for overwrite
    if not output_file and overwrite == False: 
        print("SimpleMP: Output file not specified")
        return
     
    if not os.path.exists(output_file):
        print("SimpleMP: Output file doesn't exist. Creating it...")
        with open(output_file, 'w') as f:
            pass

    input = av.open(str(input_file))

    if overwrite: 
        outputfilename = input_file

    mediatype : int = 0
    # ==== check file extenstion and codec compatibility with settings
    ext = os.path.splitext(output_file)[1].lower()
    if not check_media_compat(
        ext, 
        audio_codecname=audio_encoder, video_codecname=video_encoder, 
        samplerate=samplerate, samplefmt=sample_fmt, pixel_fmt=pixel_fmt,
        bitrate=bitrate_audio, bitrate_video=bitrate_video,
        mediatype=mediatype,
    ):
        return
    
    # unpack reesolution
    width, height = resolution

    smpcore(
                input_file, output_file, thread_count=thread_count, thread_type=thread_type, mute=mute,

                # Audio
                audio_codecname=audio_encoder, bitrate=bitrate_audio, sample_fmt=sample_fmt, sample_rate=samplerate, 

                # Video
                video_codecname=video_encoder, bitrate_vdo=bitrate_video, frame_rate=frame_rate, pixel_fmt=pixel_fmt,
                width=width, height=height, preset=preset, tune=tune, profile=profile, crf=crf,   
                mediatype=mediatype, loop=loop    
            )
