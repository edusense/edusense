# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

ARG CUDA_VERSION=10.0
ARG CUDNN_VERSION=7
ARG UBUNTU_VERSION=18.04
FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION} AS builder

WORKDIR /openpose
COPY third_party/openpose /openpose
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y --no-install-recommends install \
    ca-certificates \
    curl \
    git \
    build-essential \
    libatlas-base-dev \
    libprotobuf-dev \
    libleveldb-dev \
    libsnappy-dev \
    libhdf5-serial-dev \
    protobuf-compiler \
    libboost-all-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    liblmdb-dev \
    python-setuptools \
    python-dev \
    python3-setuptools \
    python3-dev \
    python3-pip \
    libopencv-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

RUN curl -o install_cmake.sh -SL "https://github.com/Kitware/CMake/releases/download/v3.15.4/cmake-3.15.4-Linux-x86_64.sh" && \
  /bin/bash install_cmake.sh --skip-license --prefix=/usr/local && \
  rm install_cmake.sh

COPY edusense examples/edusense
RUN patch examples/tutorial_api_cpp/16_synchronous_custom_output.cpp -i examples/edusense/edusense.cpp.patch -o examples/edusense/edusense.cpp && \
    patch examples/user_code/CMakeLists.txt -i examples/edusense/CMakeLists.txt.patch -o examples/edusense/CMakeLists.txt

COPY third_party/base64 examples/edusense/base64
COPY third_party/rapidjson/include/rapidjson examples/edusense/rapidjson
RUN echo "add_subdirectory(edusense)" >> examples/CMakeLists.txt

WORKDIR /app/build
RUN cmake /openpose && make -j 8 && make install

FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-runtime-ubuntu${UBUNTU_VERSION}

ENV DEBIAN_FRONTEND=noninteractive
# The following gosu setup procedure is derived from
# https://github.com/tianon/gosu.
RUN set -eux; \
  apt-get update; \
  apt-get install -y gosu; \
  rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
  gosu nobody true

RUN apt-get update && apt-get -y --no-install-recommends install \
    ca-certificates \
    libboost-all-dev \
    libatlas-base-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libprotobuf-dev \
    libopencv-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /app/build/examples/edusense/edusense.bin /app/
COPY --from=builder /openpose/models /app/models
COPY entrypoint.sh /app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
