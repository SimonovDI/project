FROM python:latest
WORKDIR /bot
COPY /requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt
COPY . /bot
