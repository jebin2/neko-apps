# Brave Remote Debug

Run Brave Browser inside a Neko container with remote debugging enabled and built-in ad blocking. Brave's Shields provide ad/tracker blocking out of the box — no extensions needed.

---

## 🚀 Build

Clone the `neko-apps` repository and build the image:

```bash
git clone https://github.com/m1k1o/neko-apps.git
cd neko-apps

./build --application brave-remote-debug --base_image ghcr.io/m1k1o/neko/base:latest
```

The image will be tagged as:

```
ghcr.io/m1k1o/neko-apps/brave-remote-debug:latest
```

> **Note:** Brave's APT repo supports both `amd64` and `arm64` natively — the same Dockerfile works on both architectures.

---

## ▶️ Run

Run the container with the following command:

```bash
docker run -it --rm \
  -p 8080:8080 \
  -p 9223:9223 \
  --shm-size=2gb \
  --cap-add=SYS_ADMIN \
  ghcr.io/m1k1o/neko-apps/brave-remote-debug:latest
```

This will:

* Expose the Neko web interface on port `8080`
* Expose Brave DevTools on port `9223`

---

## ⚙️ Add Custom Brave Flags

You can pass additional Brave flags using the `NEKO_BRAVE_FLAGS` environment variable. Example:

```bash
docker run -it --rm \
  -p 8080:8080 \
  -p 9223:9223 \
  --shm-size=2gb \
  --cap-add=SYS_ADMIN \
  -e NEKO_BRAVE_FLAGS="--no-sandbox --no-zygote --disable-extensions --window-size=1920,1080" \
  ghcr.io/m1k1o/neko-apps/brave-remote-debug:latest
```

---

## 📖 Documentation

For more details about Neko apps and room management, see the [Neko Documentation](https://github.com/m1k1o/neko).

---
