FROM dathan/ffmpeg-vaapi:latest

ADD . /app
WORKDIR /app

ENTRYPOINT ["/app/transcoder"]
