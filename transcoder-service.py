import glob
import os
from pathlib import Path

ARCHIVE_DIR="/volume1/Media/Archive"
PENDING_DIR=f"{ARCHIVE_DIR}/Pending"
PENDING_DVD_DIR=f"{PENDING_DIR}/DVD"
TRANSCODED_DIR=f"{ARCHIVE_DIR}/Transcoded"
STAGING_DIR=f"{ARCHIVE_DIR}/Staging"


def get_pending_dvds():
    all_files = [f for f in glob.iglob(os.path.join(PENDING_DVD_DIR,"**"), recursive=True) if Path(f).is_file()]
    all_files.sort()
    return all_files


def get_transcoded_files():
    all_files = [f for f in glob.iglob(os.path.join(TRANSCODED_DIR, "**"), recursive=True) if Path(f).is_file()]
    all_files.sort()
    return all_files


def get_really_pending_dvds():
    all_pending_dvds = [os.path.relpath(f, PENDING_DVD_DIR) for f in get_pending_dvds()]
    all_transcoded_files = [os.path.relpath(f, TRANSCODED_DIR) for f in get_transcoded_files()]
    really_pending_dvds = list(set(all_pending_dvds).difference(set(all_transcoded_files)))
    really_pending_dvds.sort()
    return really_pending_dvds

def libx264_command_line(pending_path, staging_path):
    segments = ["ffmpeg"]

    #segments.append("-t 20") # for debugging, only process the first little bit

    # TODO: without other config, the Bluey transcoding selects ~1600kbps bitrate; should we move it higher?

    segments.append(f"""-i "{pending_path}" """)

    #segments.append("-c:v libx264") # though we could consider h265?
    segments.append("-c:v libx264") # From https://trac.ffmpeg.org/wiki/Encode/H.264#Whydoesntmylosslessoutputlooklossless

    segments.append("-vf yadif=3:1") # deinterlacing

    # According to https://trac.ffmpeg.org/wiki/Encode/H.264, 17 or 18 is virtually lossless (visually)
    segments.append("-crf 18")
    segments.append("-tune animation")

    # TODO: if we see problems in the output video, add config to configure the framerate explicitly
    # Framerate is either 24fps, 25fps, or 30fps for theatrical film, European tv, and North American tv, respectively. (Except in transferring film to a tv screen, 24fps becomes 23.976fps, in most cases.) Of course 60fps is common for GoPro-like cameras, but here 30fps would be a reasonable choice.
    # From https://stackoverflow.com/a/72277037
    #segments.append("-filter:v fps=24000/1001,yadif=3:1")
    #segments.append("""-filter:v "fps=30,yadif=3:1" """)

    # TODO: check out CBR encoding: https://trac.ffmpeg.org/wiki/Encode/H.264

    #segments.append("-b:v 8500k ")

    # alternatively, choose a preset
    #segments.append("-preset ultrafast")
    segments.append("-preset veryslow")

    segments.extend([
            # These prolly aren't things we need to tweak
            "-f matroska",
            "-threads 4",
            "-c:a copy",
            "-c:s copy",
            "-progress -",
            "-stats_period 60",
            f""""{staging_path}" """
            #f"""&> "{staging_file}.log" """
    ])

    return segments

    # -profile 3 -level 41 -coder cabac -threads 4 -allow_sw:v 1 -map 0:1 -c:a:0 copy -disposition:a:0 default -map 0:6 -c:s:0 copy -disposition:s:0 0 -metadata:g title\=“If you want file title in the metadata, goes here” -default_mode passthrough ‘outfile.mkv’
    # ffmpeg -loglevel error -stats -i source.video -map 0:0 -filter:v fps\=24000/1001 -c:v h264_videotoolbox -b:v 8500k -profile 3 -level 41 -coder cabac -threads 4 -allow_sw:v 1 -map 0:1 -c:a:0 copy -disposition:a:0 default -map 0:6 -c:s:0 copy -disposition:s:0 0 -metadata:g title\=“If you want file title in the metadata, goes here” -default_mode passthrough ‘outfile.mkv’
    # potential alternative config from https://stackoverflow.com/a/72277037


def transcode_one_dvd():
    pending_dvds = get_really_pending_dvds()
    if len(pending_dvds) == 0:
        print("No pending DVDS")
        return

    pending_dvd = pending_dvds[0]
    # get an absolute reference
    pending_dvd_full_path = os.path.join(PENDING_DVD_DIR, pending_dvd)
    # get the staging file
    staging_file = os.path.join(STAGING_DIR, pending_dvd)
    staging_directory = os.path.dirname(staging_file)
    os.makedirs(staging_directory, exist_ok=True)
    if Path(staging_file).is_file():
        print(f"Removing staging file {staging_file}")
        os.remove(staging_file)

    # invoke ffmpeg
    print(f"Transcoding {pending_dvd_full_path} -> {staging_file}")
    cmd_segments = libx264_command_line(pending_dvd_full_path, staging_file)
    cmd = " ".join(cmd_segments)
    #print(f"""Would execute: ffmpeg -i "{pending_dvd_full_path}" -f matroska -threads 4 -c:v libx264 -crf 18 -c:a copy -c:s copy -progress - -stats_period 60 "{staging_file}" &> "{staging_file}.log" """)
    exit_status = os.system(cmd)
    print(f"ffmpeg exited with status {exit_status}")
    if exit_status == 0:
        # make the output directory
        target_file = os.path.join(TRANSCODED_DIR, pending_dvd)
        print(f"Moving staging file {staging_file} -> {target_file}")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        os.rename(staging_file, target_file)


if __name__ == "__main__":
    transcode_one_dvd()

# TODO: invoke ffmpeg to query the frame rate of the input video and use the same framerate on the output instead of using a default

