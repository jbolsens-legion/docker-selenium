ARG NAMESPACE=selenium
ARG BASE=base
ARG VERSION=latest
FROM ${NAMESPACE}/${BASE}:${VERSION} AS builder
ARG VERSION_FFMPEG="7.1"
ARG VERSION_RCLONE="v1.68.2"
ARG VERSION_GO="1.23.3"

USER root

#======================================
# Install build tools
#======================================
ARG TOOLS_DEPS="autoconf automake cmake libfreetype6 gcc build-essential libtool make nasm pkg-config zlib1g-dev numactl \
libnuma-dev libx11-6 libxcb1 libxcb1-dev yasm git"

RUN apt-get update -qqy \
    && apt-get -qqy --no-install-recommends install ${TOOLS_DEPS} \
    && apt-get -qyy clean \
    && mkdir -p /usr/local/src

RUN curl -sLO https://go.dev/dl/go$VERSION_GO.linux-$(dpkg --print-architecture).tar.gz \
    && tar -xf go$VERSION_GO.linux-$(dpkg --print-architecture).tar.gz -C /usr/local \
    && rm -rf go$VERSION_GO.linux-$(dpkg --print-architecture).tar.gz* \
    && ln -sf /usr/local/go/bin/go /usr/bin/go \
    && go version

RUN cd /usr/local/src \
    && git clone https://github.com/rclone/rclone.git \
    && cd rclone \
    && git checkout $VERSION_RCLONE \
    && make \
    && mv ~/go/bin/rclone /usr/local/bin/ \
    && rclone version

#======================================
# Install x264 from source
#======================================
RUN cd /usr/local/src \
    && git clone https://code.videolan.org/videolan/x264.git \
    && cd x264 \
    && ./configure --prefix="/usr/local" --enable-static \
    && make \
    && make install

#======================================
# Install FFmpeg from source
#======================================
RUN cd /usr/local/src \
    && git clone https://github.com/FFmpeg/FFmpeg.git \
    && cd FFmpeg \
    && git checkout release/$VERSION_FFMPEG \
    && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig" ./configure \
    --prefix="/usr/local" \
    --extra-cflags="-I/usr/local/include" \
    --extra-ldflags="-L/usr/local/lib" \
    --pkg-config-flags="--static" \
    --enable-gpl \
    --enable-nonfree \
    --enable-libx264 \
    --enable-libxcb \
    && make \
    && make install

RUN rm -rf /usr/local/src/* \
    && rm -rf /usr/local/go \
    && apt-get remove -y ${TOOLS_DEPS} \
    && apt-get -qyy autoremove

# Final stage
FROM ${NAMESPACE}/${BASE}:${VERSION}
ARG AUTHORS
LABEL authors=${AUTHORS}

USER root

COPY --from=builder /usr/local /usr/local

RUN apt-get -qqy update \
    && apt-get -qqy --no-install-recommends install \
    libx11-6 libxcb1 libxcb-shm0 \
    x11-xserver-utils x11-utils python3-psutil \
    && pip install --no-cache-dir --upgrade --break-system-packages setuptools \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY *.conf /etc/supervisor/conf.d/
COPY --chown="${SEL_UID}:${SEL_GID}" *.sh video_ready.py /opt/bin/

USER ${SEL_UID}

RUN ldd /usr/local/bin/ffmpeg \
    && /usr/local/bin/ffmpeg -version \
    && rclone --version \
    && touch /opt/selenium/upload.conf

ENV DISPLAY_NUM=99 \
    DISPLAY_CONTAINER_NAME="selenium" \
    SE_SERVER_PROTOCOL="http" \
    SE_VIDEO_POLL_INTERVAL=1 \
    SE_SCREEN_WIDTH=1920 \
    SE_SCREEN_HEIGHT=1080 \
    SE_FRAME_RATE=15 \
    SE_CODEC="libx264" \
    SE_PRESET="-preset ultrafast" \
    VIDEO_FOLDER="/videos" \
    SE_VIDEO_FILE_NAME=video.mp4 \
    SE_VIDEO_FILE_NAME_TRIM_REGEX="[:alnum:]-_" \
    # Environment variables for the uploader
    RCLONE_CONFIG="/opt/selenium/upload.conf" \
    SE_VIDEO_UPLOAD_ENABLED=false \
    SE_VIDEO_INTERNAL_UPLOAD=true \
    SE_UPLOAD_DESTINATION_PREFIX=""

ENTRYPOINT ["/opt/bin/entry_point.sh"]
CMD ["/opt/bin/entry_point.sh"]

EXPOSE 9000
