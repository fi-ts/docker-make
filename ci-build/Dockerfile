FROM ubuntu as builder
ENV BOOTLOADER_CC=musl-gcc
RUN apt update && apt install -y busybox musl musl-dev musl-tools liblzma-dev scons patchelf python3-pip
WORKDIR /app
COPY . .
RUN python3 -m pip install staticx pyinstaller .
RUN pyinstaller -F docker-make.spec \
 && staticx /app/dist/docker-make /app/dist/docker-make-static \
 && /app/dist/docker-make-static -v

FROM docker
RUN apk update \
 && apk add git
COPY --from=builder /app/dist/docker-make-static /docker-make
ENTRYPOINT ["/docker-make"]
