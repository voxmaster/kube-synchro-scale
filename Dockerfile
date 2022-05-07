FROM python:3.9-slim
LABEL maintainer="Oleksii Marchenko <oleksi.marchenko@gmail.com>"

WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt
CMD python3 main.py
