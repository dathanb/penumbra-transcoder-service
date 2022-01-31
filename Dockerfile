FROM jrottenberg/ffmpeg:4.4.1-ubuntu2004

ADD transcoder-service /app/
WORKDIR /app

ENTRYPOINT ["/bin/bash", "/app/transcoder-service"]
