#!/usr/bin/env bash
set -euo pipefail

# Validate SHA256 checksums for seed files
# Exit code 0 = all checksums valid
# Exit code 1 = one or more checksums invalid or files missing

echo "🔐 Validating seed file checksums..."
echo

# Known good SHA256 checksums from v1.0.0
declare -A CHECKSUMS=(
  ["golden_seed_16.bin"]="87f829d95b15b08db9e5d84ff06665d077b267cfc39a5fa13a9e002b3e4239c5"
  ["golden_seed_32.bin"]="096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f"
  ["golden_seed.hex"]="9569db82634b232aebe75ef131dc00bdd033b8127dfcf296035f53434b6c2ccd"
)

VALID=0
INVALID=0
MISSING=0

for file in "${!CHECKSUMS[@]}"; do
  expected="${CHECKSUMS[$file]}"

  if [[ ! -f "$file" ]]; then
    echo "❌ MISSING: $file"
    MISSING=$((MISSING + 1))
    continue
  fi

  actual=$(sha256sum "$file" | awk '{print $1}')

  if [[ "$actual" == "$expected" ]]; then
    echo "✅ VALID: $file"
    VALID=$((VALID + 1))
  else
    echo "❌ INVALID: $file"
    echo "   Expected: $expected"
    echo "   Got:      $actual"
    INVALID=$((INVALID + 1))
  fi
done

echo
echo "Summary:"
echo "  ✅ Valid:   $VALID"
echo "  ❌ Invalid: $INVALID"
echo "  ❓ Missing: $MISSING"

if [[ $INVALID -gt 0 ]] || [[ $MISSING -gt 0 ]]; then
  echo
  echo "⚠️  Checksum validation FAILED"
  exit 1
else
  echo
  echo "✨ All checksums valid!"
  exit 0
fi
