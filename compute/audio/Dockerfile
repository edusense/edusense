# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

FROM python:3.7-stretch
LABEL maintainer dohyunk@cs.cmu.edu

# Some part of the following setup procedure is derived from
# https://github.com/tianon/gosu/INSTALL.md.
RUN set -eux; \
  apt-get update; \
  apt-get install -y \
    gosu \
    libasound-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    libav-tools ; \
  rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
  gosu nobody true

WORKDIR /app
COPY ./python /app
COPY ./models /app/models
COPY ./entrypoint.sh /app
RUN pip install --no-cache-dir -r requirements.txt
ADD https://www.dropbox.com/s/cq1d7uqg0l28211/example_model.hdf5?dl=1 /app/models/example_model.hdf5

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
