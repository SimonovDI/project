FROM python:latest
WORKDIR .
COPY /requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt
COPY . /Web_Project



