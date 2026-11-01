# Standalone container for the Ingenium package (ingenium/).
# Works with Podman, Podman Desktop, Rancher Desktop, or Docker:
#   podman build -t ingenium -f Containerfile .
#   podman run --rm -p 8000:8000 ingenium
#   -> open http://localhost:8000 for the HTML dashboard
#
# For the one-shot CLI report instead of the web GUI:
#   podman run --rm ingenium python3 -m ingenium.demo
FROM python:3.12-slim

WORKDIR /app
COPY ingenium/ ./ingenium/

# Fail the build if the test suite doesn't pass.
RUN python3 -m unittest discover -s ingenium/tests -v

EXPOSE 8000
CMD ["python3", "-m", "ingenium.web.server"]
