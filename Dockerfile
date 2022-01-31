FROM jrottenberg/ffmpeg:latest

ADD transcoder-service /app/
WORKDIR /app

ENTRYPOINT ["/app/transcoder-service"]
