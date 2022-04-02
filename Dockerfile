FROM python:3.10.0rc2-buster

WORKDIR /

COPY requirements.txt .

RUN apt update && apt install curl && rm -rf /var/lib/apt/lists/* && \
    curl -sL https://github.com/cli/cli/releases/download/v2.7.0/gh_2.7.0_linux_amd64.tar.gz > gh.tar.gz && \
    tar xzf gh.tar.gz && \
    mv gh_2.7.0_linux_amd64/bin/gh bin/gh && \
    chmod +x bin/gh && \
    rm gh.tar.gz

RUN pip3 install -r requirements.txt && rm requirements.txt

COPY main.py .

ENV PYTHONUNBUFFERED 1

CMD python3 main.py
