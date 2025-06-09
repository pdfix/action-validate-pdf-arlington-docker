# Use the official Debian slim image as a base
FROM debian:stable-slim

# Update system and Install python3 and java
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    openjdk-17-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/validation/


# Create a virtual environment and install dependencies
ENV VIRTUAL_ENV=venv
RUN python3 -m venv venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt /usr/validation/
RUN pip install --no-cache-dir -r requirements.txt 


# Copy config
COPY config.json /usr/validation/
# Copy the source code
COPY src/ /usr/validation/src/
# Copy VeraPDF CLI program
COPY res/ /usr/validation/res/


ENTRYPOINT ["/usr/validation/venv/bin/python3", "/usr/validation/src/main.py"]
