# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

FROM python:2.7-buster AS builder
LABEL maintainer dohyunk@cs.cmu.edu

WORKDIR /app


RUN pip install virtualenv
RUN virtualenv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY third_party ./
RUN cd deepgaze && python setup.py install

FROM python:2.7-buster
# The following gosu setup procedure is derived from
# https://github.com/tianon/gosu/INSTALL.md.
RUN set -eux; \
  apt-get update; \
  apt-get install -y \
     gosu \
### this install tesseract 4.0.0 but audio uses
### 4.0.0 beeta
     tesseract-ocr; \
  rm -rf /var/lib/apt/lists/*; \
# verify that the binary works
  gosu nobody true

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY entrypoint.sh ./
COPY python ./
COPY models ./models
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["/app/entrypoint.sh"]
