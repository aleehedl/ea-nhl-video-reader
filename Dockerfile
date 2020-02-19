FROM python:latest

RUN apt-get update
RUN apt-get -y install \
    tesseract-ocr
RUN apt-get clean

RUN pip install --upgrade pip; \
    pip install \
    pillow \
    pytesseract

WORKDIR /app
