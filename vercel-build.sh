#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Install FFmpeg
# Vercel's build environment is Amazon Linux 2, so we download a static build for it.
echo "Installing FFmpeg..."
curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
# Move the ffmpeg binary to a location in the PATH
mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
# Clean up downloaded files
rm -rf ffmpeg.tar.xz ffmpeg-*-amd64-static
echo "FFmpeg installed successfully."

# 2. Build the project
echo "Collecting static files..."
python3.12 -m pip install -r requirements.txt
python3.12 manage.py collectstatic --noinput --clear
echo "Static files collected."