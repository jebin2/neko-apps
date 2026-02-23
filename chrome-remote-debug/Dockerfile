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
        # ARM64: install Chromium from Debian unstable for a recent version \
        echo 'deb http://deb.debian.org/debian unstable main' > /etc/apt/sources.list.d/unstable.list; \
        # Pin unstable low so only explicit installs pull from it \
        printf 'Package: *\nPin: release a=unstable\nPin-Priority: 100\n' > /etc/apt/preferences.d/unstable; \
        apt-get update; \
        apt-get install -y --no-install-recommends -t unstable chromium; \
        ln -sf /usr/bin/chromium /usr/bin/google-chrome; \
        # Clean up unstable source to avoid future surprises \
        rm -f /etc/apt/sources.list.d/unstable.list /etc/apt/preferences.d/unstable; \
    fi; \
    apt-get install -y --no-install-recommends openbox socat xdotool scrot xclip; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY supervisord.conf /etc/neko/supervisord/google-chrome.conf
COPY --chown=neko preferences.json /home/neko/.config/google-chrome/Default/Preferences
COPY policies.json /etc/opt/chrome/policies/managed/policies.json
COPY openbox.xml /etc/neko/openbox.xml
