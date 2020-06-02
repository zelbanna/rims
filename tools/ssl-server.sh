#!/bin/bash
#
# Generates both keys and cert
#
# $1 = CN
# $2 = AltNames
#
# subjectAltName = IP:192.168.0.1,DNS:rims.local,DNS:rims
#
echo "Creating CERT for $1 with Alternative Names '$2'"
echo ""
echo "********************* Creating Keys *********************"
openssl genrsa -out ../ssl/$1-key.pem 4096

echo "********************* CSR request ***********************"
if [ -z "$2" ]
then
 openssl req -new -subj "/C=SE/O=RIMS/CN=$1" -key ../ssl/$1-key.pem -out ../ssl/$1.csr
 openssl x509 -req -days 365 -in ../ssl/$1.csr -CA ../ca/CA-cert.pem -CAkey ../ca/CA-key.pem -CAcreateserial -out ../ssl/$1-cert.pem
else
 echo "Adding Alt name $2"
 openssl req -new -subj "/C=SE/O=RIMS/CN=$1" -addext "subjectAltName=$2" -key ../ssl/$1-key.pem -out ../ssl/$1.csr
 openssl x509 -req -extfile <(printf "subjectAltName=$2") -days 365 -in ../ssl/$1.csr -CA ../ca/CA-cert.pem -CAkey ../ca/CA-key.pem -CAcreateserial -out ../ssl/$1-cert.pem
fi
rm ../ssl/$1.csr
