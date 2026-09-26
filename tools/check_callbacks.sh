#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
H=${1:-third_party/binaryninjacore.h}
if [ ! -f "$H" ]; then
	echo "header not found: $H (run 'make header' first or pass the path)"
	exit 1
fi
abi=$(awk '/define BN_CURRENT_CORE_ABI_VERSION/ {print $3; exit}' "$H")
echo "checking $H (ABI $abi)"
missing=0
for spec in "BNCustomArchitecture src/arch.c \\." "BNCustomCallingConvention src/cc.c cb\\."; do
	set -- $spec
	s=$1 f=$2 p=$3
	pre=$(cc -E -P -Iinclude -isystem "$(dirname "$H")" -DLA_ALLOW_UNTESTED_API "$f")
	for x in $(awk "/typedef struct $s\$/,/} $s;/" "$H" | grep -oE '\(\*[[:space:]]*[A-Za-z0-9_]+\)' | tr -d '(*) '); do
		if ! printf '%s\n' "$pre" | grep -qE "(^|[^A-Za-z0-9_])$p$x[[:space:]]*="; then
			echo "  missing: $s.$x (in $f)"
			missing=$((missing + 1))
		fi
	done
done
if [ "$missing" -eq 0 ]; then
	echo "  all callbacks are set"
else
	echo "  $missing callback(s) missing"
	exit 1
fi
