FROM python:3.8.5

WORKDIR usr/src/nwb_web_gui
# Various Python and C/build deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ \
        libtiff5-dev

RUN mkdir files
COPY requirements.txt .
RUN pip install numpy && pip install --no-cache-dir -r requirements.txt
COPY requirements.txt .
RUN cp ../../include/x86_64-linux-gnu/tiff.h ../../local/include
COPY . .

EXPOSE 5000
EXPOSE 8866

CMD gunicorn -w 1 -b 0.0.0.0:5000 wsgi:app