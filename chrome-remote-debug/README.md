# Chrome Remote Debug

Run Google Chrome inside a Neko container with remote debugging enabled and accessible from a browser. This app is useful for testing, automation, and accessing Chrome DevTools externally.

---

## Build

Clone the `neko-apps` repository and build the image:

```bash
git clone https://github.com/jebin2/neko-apps.git
cd neko-apps

./build --application chrome-remote-debug --base_image ghcr.io/m1k1o/neko/base:latest
```

The image will be tagged as:

```
ghcr.io/jebin2/neko-apps/chrome-remote-debug:latest
```

---

## Run

```bash
docker run -it --rm \
  -p 8080:8080 \
  -p 9223:9223 \
  --shm-size=2gb \
  --cap-add=SYS_ADMIN \
  ghcr.io/jebin2/neko-apps/chrome-remote-debug:latest
```

This will:

* Expose the Neko web interface on port `8080`
* Expose Chrome DevTools on port `9223`

---

## Add Custom Chrome Flags

You can pass additional Chrome flags using the `NEKO_CHROME_FLAGS` environment variable:

```bash
docker run -it --rm \
  -p 8080:8080 \
  -p 9223:9223 \
  --shm-size=2gb \
  --cap-add=SYS_ADMIN \
  -e NEKO_CHROME_FLAGS="--no-sandbox --no-zygote --disable-extensions --window-size=1920,1080" \
  ghcr.io/jebin2/neko-apps/chrome-remote-debug:latest
```

---

## Special Thanks

Thanks to [@Nefaris](https://github.com/Nefaris) — your [comment](https://github.com/m1k1o/neko/issues/391#issuecomment-3016080496) really helped get this working.

---

## Documentation

For more details about Neko apps and room management, see the [Neko Documentation](https://github.com/m1k1o/neko).
