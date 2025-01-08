FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV FLUTTER_HOME=/opt/flutter
ENV PATH=/home/developer/.local/bin:${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${FLUTTER_HOME}/bin

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Java options
ENV _JAVA_OPTIONS="-Xmx2g -Xms512m"

# Download and install Android SDK
RUN curl -o cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip \
    && mkdir -p ${ANDROID_HOME}/cmdline-tools \
    && unzip cmdline-tools.zip -d ${ANDROID_HOME}/cmdline-tools \
    && mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest \
    && rm cmdline-tools.zip

# Accept licenses and install required Android SDK packages
RUN yes | sdkmanager --licenses \
    && sdkmanager "platform-tools" \
    "platforms;android-34" \
    "build-tools;34.0.0" \
    "ndk;25.1.8937393"

# Create non-root user
RUN useradd -ms /bin/bash developer
RUN mkdir -p /home/developer/app
RUN mkdir -p ${FLUTTER_HOME}
RUN chown -R developer:developer /home/developer
RUN chown -R developer:developer ${ANDROID_HOME}
RUN chown -R developer:developer ${FLUTTER_HOME}

# Switch to developer user
USER developer
WORKDIR /home/developer/app

# Install Flutter
RUN git clone -b stable https://github.com/flutter/flutter.git ${FLUTTER_HOME} \
    && flutter doctor \
    && flutter config --no-analytics \
    && flutter config --enable-android

# Copy requirements.txt and install Python dependencies
COPY --chown=developer:developer requirements.txt .
RUN pip3 install --user -r requirements.txt \
    && python3 -m pip install --user --upgrade pip \
    && python3 -m pip install --user flet-cli

# Set the entrypoint to run Flet build
ENTRYPOINT ["bash", "-c", "flet build apk"]