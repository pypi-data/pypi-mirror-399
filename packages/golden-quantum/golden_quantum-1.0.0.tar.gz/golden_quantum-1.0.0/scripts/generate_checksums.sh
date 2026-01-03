#!/usr/bin/env bash
set -euo pipefail

# Generate SHA256 and SHA512 checksums for published assets
OUT=checksums.txt
echo "Generating checksums into $OUT"
rm -f "$OUT"

# List of assets to include
assets=(
  "golden_seed_16.bin"
  "golden_seed_32.bin"
  "golden_seed.hex"
)

for f in "${assets[@]}"; do
  if [[ -f "$f" ]]; then
    sha256sum "$f" >> "$OUT"
  fi
done

echo "\nSHA512 hashes:" >> "$OUT"
for f in "${assets[@]}"; do
  if [[ -f "$f" ]]; then
    sha512sum "$f" >> "$OUT"
  fi
done

echo "Checksums written to $OUT"
