FROM jrottenberg/ffmpeg:latest

ADD . /app
WORKDIR /app

ENTRYPOINT ["/app/transcoder-service"]
