#!/bin/bash

# Generate SSL test certificates for MCP server testing
# This script creates self-signed certificates for testing purposes only

set -e

CERT_DIR="$(dirname "$0")"
cd "$CERT_DIR"

echo "🔐 Generating SSL test certificates..."

# Generate private key for CA
openssl genrsa -out ca-key.pem 4096

# Generate CA certificate
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca-cert.pem -subj "/C=US/ST=Test/L=Test/O=MCP Test CA/CN=Test CA"

# Generate private key for server
openssl genrsa -out server-key.pem 4096

# Generate certificate signing request for server
openssl req -subj "/C=US/ST=Test/L=Test/O=MCP Test Server/CN=localhost" -new -key server-key.pem -out server.csr

# Generate server certificate signed by CA
openssl x509 -req -days 365 -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -out server-cert.pem -extensions v3_req -extfile <(
cat <<EOF
[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
)

# Generate self-signed certificate (for testing self-signed scenarios)
openssl req -x509 -newkey rsa:4096 -nodes -out selfsigned-cert.pem -keyout selfsigned-key.pem -days 365 -subj "/C=US/ST=Test/L=Test/O=MCP Test/CN=localhost"

# Generate expired certificate (for testing expired scenarios)
# Create a certificate that expires immediately
openssl req -x509 -newkey rsa:2048 -nodes -out expired-cert.pem -keyout expired-key.pem -days 1 -subj "/C=US/ST=Test/L=Test/O=MCP Expired/CN=localhost"
# Backdate it to make it expired
touch -t 202301010000 expired-cert.pem 2>/dev/null || true

# Generate invalid certificate (corrupted)
echo "-----BEGIN CERTIFICATE-----
INVALID_CERTIFICATE_DATA
-----END CERTIFICATE-----" > invalid-cert.pem

# Set appropriate permissions
chmod 600 *.pem
chmod 644 *-cert.pem ca-cert.pem selfsigned-cert.pem expired-cert.pem invalid-cert.pem

# Clean up temporary files
rm -f server.csr

echo "✅ SSL test certificates generated successfully:"
echo "  📁 CA Certificate: ca-cert.pem"
echo "  🔑 CA Key: ca-key.pem" 
echo "  📜 Server Certificate: server-cert.pem"
echo "  🗝️  Server Key: server-key.pem"
echo "  🔒 Self-signed Certificate: selfsigned-cert.pem"
echo "  🔓 Self-signed Key: selfsigned-key.pem"
echo "  ⏰ Expired Certificate: expired-cert.pem"
echo "  ❌ Invalid Certificate: invalid-cert.pem"
echo ""
echo "These certificates are for TESTING ONLY - do not use in production!"