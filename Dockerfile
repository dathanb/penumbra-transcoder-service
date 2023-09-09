FROM jrottenberg/ffmpeg:5-centos

CMD mkdir -p /volume1/Media/Archive
ADD transcoder-service.py /app/
WORKDIR /app

ENTRYPOINT ["/usr/libexec/platform-python3.6", "/app/transcoder-service.py"]
