ARG BASE_IMAGE=ghcr.io/m1k1o/neko/base:latest
FROM $BASE_IMAGE

RUN set -eux; \
    apt-get update; \
    ARCH="$(dpkg --print-architecture)"; \
    if [ "$ARCH" = "amd64" ]; then \
        wget -O /tmp/google-chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"; \
    dpkg -i /tmp/google-chrome.deb || true; \
    apt-get install -fy --no-install-recommends; \
        rm /tmp/google-chrome.deb; \
    else \
        # ARM64 fallback: install Chromium and symlink it as google-chrome
        apt-get install -y --no-install-recommends chromium; \
        ln -sf /usr/bin/chromium /usr/bin/google-chrome; \
    fi; \
    apt-get install -y --no-install-recommends openbox socat xdotool scrot xclip; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY supervisord.conf /etc/neko/supervisord/google-chrome.conf
COPY --chown=neko preferences.json /home/neko/.config/google-chrome/Default/Preferences
COPY policies.json /etc/opt/chrome/policies/managed/policies.json
COPY openbox.xml /etc/neko/openbox.xml
