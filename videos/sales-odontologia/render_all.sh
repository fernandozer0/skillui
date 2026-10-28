#!/bin/sh
# Render reelN.html + musicN.wav into sales-odontologia-reels-vN.mp4 for each N given.
set -e
cd "$(dirname "$0")"
for n in "$@"; do
  PAGE=reel$n.html node render.js reel${n}_silent.mp4 2>&1 | grep -E "Error|kb/s" || true
  ffmpeg -loglevel error -y -i reel${n}_silent.mp4 -i music$n.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart sales-odontologia-reels-v$n.mp4
  echo "done v$n"
done
