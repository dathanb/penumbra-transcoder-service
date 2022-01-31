At this point, only `transcoder_service` contains used code. The other files
are just here for reference.

But on the other hand, the files are consistent with the ffmpeg instruction used in the `transcode_service`,
so they should be runnable as a one-off with similar results.

To run, first run `./build`, which will build a Docker container for the
transcoder service; then run `./start_transcoder_service`, which will start the
service.
