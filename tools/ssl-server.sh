#!/bin/bash
#
# Generates both keys and cert
#
# $1 = CN
# $2 = AltNames
#
echo "Creating CERT for $1 with Alternative Names $2"
echo ""
echo "********************* Creating Keys *********************"
openssl genrsa -out ../ssl/$1-key.pem 4096

echo "********************* CSR request ***********************"
echo " -Do not assign password to cert! Press key to continue -"
read
openssl req -new -subj "/C=SE/O=RIMS/CN=$1" -key ../ssl/$1-key.pem -out ../ssl/$1.csr

echo "********************* CA signing ************************"
openssl x509 -req -days 365 -in ../ssl/$1.csr -CA ../ca/CA-cert.pem -CAkey ../ca/CA.key -CAcreateserial -out ../ssl/$1-cert.pem
rm ../ssl/$1.csr
