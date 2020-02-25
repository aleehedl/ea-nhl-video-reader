FROM tensorflow/tensorflow:2.1.0-py3

RUN apt-get update
RUN apt-get -y install \
    ffmpeg \
    tesseract-ocr
RUN apt-get clean

RUN pip install --upgrade pip; \
    pip install \
    ffmpeg-python \
    pillow \
    pytesseract \
    youtube-dl

WORKDIR /app
