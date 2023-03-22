FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# # Install X Window System and dependencies
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends x11-xserver-utils scrot python3-tk \
#     && rm -rf /var/lib/apt/lists/*
#
# # Set up X11 forwarding
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         xauth \
#         x11-apps \
#         xvfb \
#     && rm -rf /var/lib/apt/lists/*
#
# RUN mkdir -p /etc/ssh/
# RUN echo "X11UseLocalhost no" >> /etc/ssh/sshd_config
#
# RUN echo "export DISPLAY=:0" >> /root/.bashrc

WORKDIR /app
ADD requirements.txt /requirements.txt

RUN pip install virtualenvwrapper
RUN python3 -m venv /venv
RUN /venv/bin/pip install -U pip
RUN /venv/bin/pip install --no-cache-dir -r /requirements.txt
