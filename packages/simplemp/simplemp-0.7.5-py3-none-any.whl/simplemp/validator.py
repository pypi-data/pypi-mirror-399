from math import log
from .logs import logstring

# don't remove . from keys. It's for explicitly describing extension name
codec_dict = {

    # Audio

    ".3gp"  : ["aac"],
    ".aac"  : ["aac"],
    ".adts" : ["aac"],
    ".aif"  : ["pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24be", "pcm_s32be"],

    # aifc also supports alac coded but needs AIFF-C muxer. Which is unavailable in pyav
    ".aifc" : ["pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24be", "pcm_s32be"],

    ".aiff" : ["pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24be", "pcm_s32be"],

    ".flac" : ["flac"],
    ".m4a"  : ["aac", "alac"],
    ".mp3"  : ["mp3"],
    ".oga"  : ["vorbis", "opus", "flac", "speex"],
    ".ogg"  : ["vorbis", "opus", "flac", "speex"],
    ".opus" : ["opus"],
    ".wav"  : ["pcm_alaw", "pcm_mulaw",  
               "pcm_s16le", "pcm_s24le", "pcm_s32le", "pcm_s16be"], 
    # wma format also supports wmapro and wmalossless codec. But not available by default for being proprietary
    ".wma"  : ["wmav1", "wmav2"],

    # Video

    ".asf"  : ["wmv1", "wmv2",
               "aac", "flac", "mp3", "pcm_alaw", "pcm_mulaw", "pcm_s16le", "wmav1", "wmav2"],

    ".avi"  : ["mpeg4", "h264", "hevc",
               "aac", "flac", "mp3", "pcm_alaw", "pcm_mulaw", "pcm_s16le", "pcm_s24le", "pcm_s32le", "vorbis", "wmav1", "wmav2"],

    ".flv"  : ["flv", "h264",
               "aac", "mp3", "opus"],

    ".m4v"  : ["h264", "mpeg4",
               "aac", "alac"],

    ".mov"  : ["h264", "hevc", "mpeg4",
               "aac", "alac", "mp3", "pcm_alaw", "pcm_mulaw", "pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24le", "pcm_s24be", "pcm_s32le", "pcm_s32be"],

    ".mp4"  : ["h264", "hevc", "mpeg4", "av1",
               "aac", "alac", "flac", "mp3", "opus", 
               "pcm_alaw", "pcm_mulaw", "pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24le", "pcm_s24be", "pcm_s32le", "pcm_s32be", 
               "speex", "vorbis", "wmav1", "wmav2"],

    ".mpg"  : ["mpeg1video", "mpeg2video",
               "mp3", "pcm_s16be" ],

    ".mpeg" : ["mpeg1video", "mpeg2video",
               "mp3", "pcm_s16be"],

    ".mkv"  : ["h264", "hevc", "mpeg4",
               "aac", "alac", "flac", "mp3", "opus", "pcm_s16le", "pcm_s16be", "pcm_s24le", "pcm_s24be", "pcm_s32le", "pcm_s32be"], 

    ".ts"   : ["h264", "hevc", "mpeg2video",
               "aac", "alac", "mp3", "pcm_alaw", "pcm_mulaw", "pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24le", "pcm_s24be", "pcm_s32le", "pcm_s32be", "wmav1", "wmav2"],

    # Extremely slow if wrong settings used
    ".webm" : ["vp8", "vp9", "av1",
               "opus", "vorbis"], 
    ".wmv"  : ["wmv1"
               "aac", "flac", "mp3", "pcm_alaw", "pcm_mulaw", "pcm_s16le", "pcm_s24be", "pcm_s32be", "wmav1", "wmav2"],
}

audio_codecs = {
    "aac", "alac", "flac", "mp3", "opus",
    "pcm_alaw", "pcm_mulaw", "pcm_s8", "pcm_s16le", "pcm_s16be", "pcm_s24le", "pcm_s24be", "pcm_s32le", "pcm_s32be", 
    "speex", "vorbis", "wmav1", "wmav2"
}

video_codecs = {
    "av1", "flv", "h264", "hevc", "mpeg1video", "mpeg2video", "mpeg4", "vp8", "vp9", "wmv1", "wmv2"
}

bitrate_range_dict = {

    # Compressed audio codecs
    "aac": [64000, 320000],
    "mp3": [64000, 320000],
    "opus": [500, 256000],          # 0.5 kbps → 256 kbps
    "vorbis": [36000, 380000],     
    "speex": [2000, 44100],        # Narrowband / wideband

    # wma supports some more bitrates but channel specific
    "wmav1": [32000, 32000], 
    "wmav2": [32000, 32000], 

    "wmapro": [12000, 384000], 
    "wmalossless": [12000, 384000], # technically lossless can vary
}

samplerate_range_dict = {

    # Lossy
    "aac": [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 64000, 88200, 96000],
    "mp3": [32000, 48000],
    "opus": [48000, 48000],
    "vorbis": [48000, 48000],
    "speex": [8000, 32000],
    "wmav1": [8000, 11025, 16000, 22050, 32000, 44100],
    "wmav2": [8000, 11025, 16000, 22050, 32000, 44100, 48000],

    # Lossless / PCM
    "alac": [8000, 192000],
    "flac": [8000, 192000],
    "pcm_alaw": [8000, 192000],
    "pcm_mulaw": [8000, 192000],
    "pcm_s8": [8000, 192000],
    "pcm_s16le": [8000, 192000],
    "pcm_s24le": [8000, 192000],
    "pcm_s32le": [8000, 192000],
    "pcm_s16be": [8000, 192000],
    "pcm_s24be": [8000, 192000],
    "pcm_s32be": [8000, 192000],
}

codec_channels_dict = {

    # Lossy codecs

    "aac": [1, 2, 6, 8],
    "mp3": [1, 2],
    "opus": [1, 2, 6, 8],
    "vorbis": [1, 2, 6],
    "speex": [1],
    "wmav1": [1, 2],
    "wmav2": [1, 2, 6],

    # Lossless / PCM codecs

    "alac": [1, 2, 6, 8],
    "flac": [1, 2, 6, 8],
    "pcm_alaw": [1, 2],
    "pcm_mulaw": [1, 2],

    # PCM integer LE/BE: FFmpeg supports up to 8
    "pcm_s8": [1, 2, 6, 8],
    "pcm_s16le": [1, 2, 6, 8],
    "pcm_s24le": [1, 2, 6, 8],
    "pcm_s32le": [1, 2, 6, 8],
    "pcm_s16be": [1, 2, 6, 8],
    "pcm_s24be": [1, 2, 6, 8],
    "pcm_s32be": [1, 2, 6, 8],

    # PCM float: same
    "pcm_f32": [1, 2, 6, 8],
    "pcm_f64": [1, 2, 6, 8],
}


audio_sample_fmt_dict = {

    # Uncompressed PCM
    "pcm_s8": ["u8"],
    "pcm_s16le": ["s16"],
    "pcm_s16be": ["s16"],

    # FFmpeg does not expose native s24 sample_fmt
    "pcm_s24le": ["s32", "s32p"],  
    "pcm_s24be": ["s32", "s32p"],
    "pcm_s32le": ["s32", "s32p"],
    "pcm_s32be": ["s32", "s32p"],
    "pcm_f32le": ["flt", "fltp"],
    "pcm_f32be": ["flt", "fltp"],
    "pcm_f64le": ["dbl", "dblp"],
    "pcm_f64be": ["dbl", "dblp"],
    "pcm_alaw": ["s16", "s16p"],
    "pcm_mulaw": ["s16", "s16p"],

    # Lossless compressed codecs
    "flac": ["s16", "s32"],
    "alac": ["s16", "s16p", "s32", "s32p", "flt", "fltp"],


    # Lossy codecs — sample_fmt fixed, reject others
    # They do *not* accept arbitrary formats
    "aac": ["u8",  "s16",  "s16p", "s32",  "s32p", "flt", "fltp", "dbl", "dblp"],
    "mp3": ["s16p", "s16", "flt", "fltp"],
    "opus": ["flt"],
    "vorbis": ["fltp"],
    "speex": ["flt", "fltp"],
    "wmav1": ["s16"],
    "wmav2": ["s16"],
}

# Check pixel formant against codecs and extensions
pixel_fmt_dict = {

    # Check against codecs
    "av1": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],

    "h264": ["yuv420p", "yuv422p", "yuv444p", "nv12"],
    "libx264": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le", "nv12"],
    "libopenh264": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le", "nv12"],

    "h265": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],
    "hevc": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],
    "libx265": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],

    "vp8": ["yuv420p", "yuv422p", "yuv444p"],
    "vp9": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],

    "flv": ["yuv420p"],
    "mpeg1video": ["yuv420p"],
    "mpeg2video": ["yuv420p"],
    "mpeg4": ["yuv420p"],
    "wmv1" : ["yuv420p"],
    "wmv2" : ["yuv420p"],

    # Check against extensions
    ".asf": ["yuv420p"],
    ".avi": ["yuv420p", "nv12"],
    ".flv": ["yuv420p", "nv12"],
    ".m4v": ["yuv420p", "nv12"],
    ".mkv": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le", "nv12"],
    ".mov": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le", "nv12"],
    ".mp4": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "nv12"],
    ".mpg": ["yuv420p"],
    ".mpeg": ["yuv420p"],
    ".ts": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "nv12"],
    ".webm": ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],
    ".wmv": ["yuv420p"],
}


frame_rate_dict = {
    "mpeg4" : [24, 120],
    "wmv1" : [24, 30],
    "wmv2" : [24, 30],
}

preset_list = {"veryslow", "slower", "slow", "medium", "fast", "faster", "veryfast", "superfast", "ultrafast"}
profile_list = {"baseline", "high", "main"}
tune_list = {"animation", "fastdecode", "film", "grain", "stillimage", "zerolatency"}

# list of video codecs that support crf, preset, profile and tune
codec_cppt_support_list = {"h264"}
# list of video codecs that support crf, preset and profile but not tune
codec_cpp_support_list = {"av1"}


media_type_ext_dict = {
    "audio": [
        ".3gp", ".aac", ".adts", ".aif", ".aifc", ".aiff", ".alac", ".amr", ".awb", 
        ".flac", 
        ".m4a", ".mp3", "mp4", 
        ".oga", ".ogg", ".opus", 
        ".wav", ".wma" 
    ],
    
    "video": [
        ".asf", ".avi",
        ".flv",
        ".m4v" , ".mkv", ".mov", ".mp4", ".mpg", ".mpeg",
        ".ts",
        ".webm", ".wmv",
    ],
}

def check_codec_compat(ext : str, codecname : str) -> bool:

    # 1: Check extension
    if ext not in codec_dict : 
        logstring = f"SimpleMP: Unknownn media file extension: {codecname}"
        print(logstring)
        return False

    if codecname == "": return True     # in case of defaults

    # 2: Check codec existence
    all_codecs = {c for codecs in codec_dict.values() for c in codecs}
    if codecname not in all_codecs:
        logstring = f"SimpleMP: Unknown codec found: {codecname}"
        print(logstring)
        return False

    # 3: Check codec compatibility with file extension
    if codecname not in codec_dict[ext]: 
        logstring = f"SimpleMP: Unsupported codec[{codecname}] for converstion to {ext}\nSupported codecs are:\n{codec_dict[ext]}"
        print(logstring)
        return False

    return True

def check_audio_codec(codecname : str) -> bool: 

    if codecname == "": return True     # in case of defaults

    if codecname not in audio_codecs:
        logstring = f"SimpleMP: Unknown audio codec[{codecname}] found: {codecname}"
        print(logstring)
        return False
    
    return True

def check_bitrate_compat(codecname : str, bitrate : int) -> bool:

    # irrelevant for lossless codecs
    if bitrate_range_dict.get(codecname) is None: 
        return True

    if bitrate < bitrate_range_dict[codecname][0] or bitrate > bitrate_range_dict[codecname][1]: 
        logstring = (f"SimpleMP: Bitrate outside safe range for codec: {codecname}\n"
            f"Safe range: [{bitrate_range_dict[codecname][0]},{bitrate_range_dict[codecname][1]}]")
        print(logstring)
        return False

    return True

def check_samplerate_compat(codecname : str, samplerate) -> bool:
        
    if codecname == "aac" or codecname == "wmav1" or codecname == "wmav2" or codecname == "mp3":
        if samplerate not in samplerate_range_dict[codecname]: 
            logstring = (f"SimpleMP: {codecname} only supports following sample rates:\n"
                  f"{samplerate_range_dict[codecname]}")
            print(logstring)
            return False
        return True


    if samplerate < samplerate_range_dict[codecname][0] or samplerate > samplerate_range_dict[codecname][1]: 
        logstring = (f"SimpleMP: Sample rate outside safe range for codec: {codecname}\n"
              f"Safe range: [{samplerate_range_dict[codecname][0]},{samplerate_range_dict[codecname][1]}]")
        print(logstring)
        return False

    return True

def check_samplefmt_compat(codecname : str, sample_fmt : str) -> bool:

    # if not set, default will be used
    if sample_fmt == "":
        return True

    # irrelevant for lossy codecs
    if audio_sample_fmt_dict.get(codecname) is None: 
        return True

    if sample_fmt not in audio_sample_fmt_dict[codecname]:
        logstring = (f"SampleMP: Incompatible sample format: {sample_fmt} for codec: {codecname}\n"
              "Supported sample formats: \n"
              f"{audio_sample_fmt_dict[codecname]}") 
        print(logstring)
        return False
    
    return True 

def check_pixfmt_compat(ext, codecname, pixel_fmt) -> bool:

    if pixel_fmt not in pixel_fmt_dict[ext]: 
        logstring = (f"SampleMP: Incompatible sample format for extension: {ext}\n"
              "Supported sample formats: \n"
              f"{pixel_fmt_dict[ext]}") 
        print(logstring)
        return False

    if pixel_fmt not in pixel_fmt_dict[codecname]:
        logstring = (f"SampleMP: Incompatible sample format for codec: {codecname}\n"
              "Supported sample formats: \n"
              f"{pixel_fmt_dict[codecname]}") 
        print(logstring)
        return False
    
    return True 



def check_media_compat(ext : str, 
                            audio_codecname : str, video_codecname : str,
                            samplerate, samplefmt : str, pixel_fmt : str,
                            bitrate : int, bitrate_video : int,
                            mediatype : int) -> bool: 

    mediatype = -1

    if ext in media_type_ext_dict["audio"]: mediatype = 0
    if ext in media_type_ext_dict["video"]: mediatype = 1

    print(f"File extension: {ext}")
    
    match mediatype: 
        # Audio
        case 0:
            if not check_codec_compat(ext, audio_codecname):  return False
            if not check_bitrate_compat(audio_codecname, bitrate): return False
            if not check_samplerate_compat(audio_codecname, samplerate): return False
            if not check_samplefmt_compat(audio_codecname, samplefmt): return False
    
        # Video (check both audio and video for streams)
        case 1: 
            if audio_codecname != "":
                if not check_audio_codec(audio_codecname) : return False
                if not check_bitrate_compat(audio_codecname, bitrate): return False
                if not check_samplerate_compat(audio_codecname, samplerate): return False
                if not check_samplefmt_compat(audio_codecname, samplefmt): return False

            if not check_codec_compat(ext, video_codecname): return False
            if not check_codec_compat(ext, audio_codecname): return False
            if not check_bitrate_compat(video_codecname, bitrate_video): return False
            if not check_pixfmt_compat(ext, video_codecname, pixel_fmt): return False

        case _:
            print("SimpleMP: Unknonwn or unsupported media type detected")
            return False

    return True


# check video codec's compatibility with crf, preset, profile and tune
def check_CPPT_compat(codecname : str, crf : int, profile : str, preset : str, tune : str) ->  bool:

    if codecname not in codec_cppt_support_list and codecname not in codec_cpp_support_list: 
        logstring = (f"SimpleMP: Codec: {codecname} doesn't support crf, preset, profile and tune")
        print(logstring)
        return False
    
    if crf not in range(0, 51):
        logstring = (f"SimpleMP: crf outside practical range [0, 51]")
        print(logstring)
        return False 
    
    if profile not in profile_list: 
        logstring = (f"SimpleMP: Profile: {profile} is unavailable to use or unavailable or non-exitentn\n"
              f"Available: {profile_list}")
        print(logstring)
        return False
    
    if preset not in preset_list: 
        logstring = (f"SimpleMP: Preset: {preset} is unavailable to use or unavailable or non-exitent\n"
              f"Available: {preset_list}")
        print(logstring)
        return False

    if tune not in tune_list: 
        logstring = (f"SimpleMP: Profile: {profile} is unavailable to use or unavailable or non-exitent\n"
              f"Available : {tune_list}")
        print(logstring)
        return False
    
    if tune in tune_list and codecname in codec_cpp_support_list:
        logstring = (f"SimpleMP: Codec: {codecname} doesn't support tune")
        print(logstring)
        return False

    return True


def check_audio_video_compat():
    pass