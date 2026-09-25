#!/usr/bin/env bash
# generate_certs.sh — Generate self-signed TLS certificates for development.

set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-certs/local}"
COUNTRY="${COUNTRY:-US}"
STATE="${STATE:-State}"
LOCALITY="${LOCALITY:-City}"
ORG="${ORG:-LinkBridge}"
CN="${CN:-localhost}"

mkdir -p "$OUTPUT_DIR"

openssl req -x509 -newkey rsa:3072 \
    -keyout "$OUTPUT_DIR/server.key" \
    -out "$OUTPUT_DIR/server.crt" \
    -days 365 \
    -nodes \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORG/CN=$CN" \
    -addext "subjectAltName=DNS:$CN,DNS:localhost,IP:127.0.0.1"

echo "Certificates generated in $OUTPUT_DIR/"
echo "  - server.crt  (public certificate)"
echo "  - server.key  (private key)"
echo ""
echo "For production, use Let's Encrypt or your CA."
