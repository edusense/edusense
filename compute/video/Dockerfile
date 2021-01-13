# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

FROM nvidia/cuda:10.2-base
LABEL maintainer pdheer@andrew.cmu.edu


RUN set -eux; \
  apt-get update; \
  apt-get install -y software-properties-common; \
  apt-get install -y \
     gosu \
  ffmpeg \
  libsm6 \
  libxext6 \ 
  python3.7 \
  python3-pip \   
  tesseract-ocr; \
  rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
  gosu nobody true


WORKDIR /app

COPY requirements.txt ./
COPY third_party ./
COPY entrypoint.sh ./
COPY python ./
COPY models ./models

RUN cd deepgaze && python3 setup.py install
RUN pip3 install -r requirements.txt
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
