FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1

#ENV C_FORCE_ROOT true

#ENV APP_USER myapp
ENV APP_ROOT /code
ENV DEBUG True

RUN mkdir /code;

RUN apt-get update && \
    apt-get install -y \
        unzip \
        libglib2.0-0 \
        libnss3 \
        libgconf-2-4 \
        libfontconfig \
        wget \
        gnupg \
        gcc && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver


WORKDIR ${APP_ROOT}

RUN mkdir /config
ADD requirements.txt /config/
RUN pip install --no-cache-dir -r /config/requirements.txt

#USER ${APP_USER}
ADD . ${APP_ROOT}
