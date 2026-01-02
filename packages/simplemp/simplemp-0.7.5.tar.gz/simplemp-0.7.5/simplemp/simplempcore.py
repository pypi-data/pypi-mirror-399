import av
from av.audio.stream import AudioStream
from av.audio.resampler import AudioResampler
from av.video.stream import VideoStream
from av.subtitles.stream import SubtitleStream
from av.container import InputContainer, OutputContainer

from typeguard import typechecked
from typing import cast

from fractions import Fraction

from .validator import codec_cppt_support_list, codec_cpp_support_list

@typechecked
def processMedia(
        incontainer : InputContainer,
        outcontainer : OutputContainer,
        mediatype : int,
        stream_map = {},
        width : int = 800, 
        height : int = 600,
        mute : bool = False,
        loop : int = 0,
):
    print("Start processing...")

    for _ in range(loop):
        incontainer.seek(0)

        for packet in incontainer.demux():
        
            if packet.stream_index not in stream_map:
                continue

            info = stream_map[packet.stream_index]

            if packet.stream.type in ("audio", "video", "subtitle"):
                for frame in packet.decode():

                    if info["type"] == "audio":
                        if not mute: 
                            frame = info["resampler"].resample(frame)
                            for f in frame:
                                for outpacket in info["ostream"].encode(f):
                                    outcontainer.mux(outpacket)

                    elif info["type"] == "video": 
                        rescaled_frame = frame.reformat(width=width, height=height, format="yuv420p") # type: ignore
                        for outpacket in info["ostream"].encode(rescaled_frame):
                            outcontainer.mux(outpacket)
            
                    elif info["type"] == "subtitle":
                        outcontainer.mux(packet)

    # Flush all streams
    for info in stream_map.values():
        for packet_out in info["ostream"].encode(None):
            outcontainer.mux(packet_out)

@typechecked
def smpcore(
        inputfilename : str,
        outputfilename : str,
        thread_count : int, 
        thread_type : str,
        mute : bool,
        loop : int,

        # Audio
        audio_codecname : str,
        bitrate : int, 
        sample_rate : int, 
        sample_fmt : str,

        # Video
        video_codecname : str,
        bitrate_vdo : int,
        frame_rate: int,
        width : int, 
        height : int,
        pixel_fmt : str,
        preset : str, 
        tune : str, 
        profile : str, 
        crf : int, 

        mediatype : int,
):
    
    incontainer = av.open(inputfilename)
    outcontainer = av.open(outputfilename, mode="w")

    # map media stream (audio / video / subtitle) to output streams
    stream_map = {}

    for istreams in incontainer.streams:
      
        if istreams.type == "audio" and audio_codecname != "": 
            print('Audio stream will be used')
            ostreama = cast(AudioStream, outcontainer.add_stream(
                codec_name=audio_codecname,
                rate=sample_rate, 
            ))
            
            ostreama.bit_rate = bitrate
            ostreama.codec_context.thread_count = thread_count
            ostreama.codec_context.thread_type = thread_type
            
            resampler = AudioResampler(
                format=sample_fmt, 
                rate=sample_rate,
            )
            stream_map[istreams.index] = { "type": "audio", "ostream":ostreama, "resampler":resampler}

        elif istreams.type == "subtitle":
            print('Subtitles stream will be used')
            ostreams = cast(SubtitleStream, outcontainer.add_stream_from_template(istreams))
            stream_map[istreams.index] = {"type":"subtitle", "ostream":ostreams}

        elif istreams.type == "video" and video_codecname != "": 
            print('Video stream will be used')
            ostreamv = cast(VideoStream, outcontainer.add_stream(
                codec_name=video_codecname,
                rate=frame_rate,
            ))
            ostreamv.bit_rate = bitrate_vdo 

            if video_codecname in codec_cppt_support_list: 
                ostreamv.options = {"crf":str(crf), "preset":preset, "profile":profile, "tune":tune}

            if video_codecname in codec_cpp_support_list: 
                ostreamv.options = {"crf":str(crf), "preset":preset, "profile":profile}

            ostreamv.pix_fmt=pixel_fmt
            ostreamv.height=height
            ostreamv.width=width
            ostreamv.time_base = Fraction(1, frame_rate)
            
            stream_map[istreams.index] = {"type":"video", "ostream":ostreamv}

        else: 
            print(f'SimpleMP: Unknown media stream detected\nType:{istreams.type}\n')


    processMedia(incontainer, outcontainer, mediatype, stream_map, width, height, mute, loop=loop)
    
    incontainer.close()
    outcontainer.close()