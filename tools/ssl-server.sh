#!/bin/bash
#
# Generates both keys and cert
#
echo "********************* Creating Keys *********************"
openssl genrsa -aes256 -out ../ssl/$1-key.pem 4096

echo "********************* CSR request ***********************"
echo " -Do not assign password to cert! Press key to continue -"
read
openssl req -new -key ../ssl/$1-key.pem -out ../ssl/$1.csr

echo "********************* CA signing ************************"
#openssl x509 -req -days 365 -in ../ssl/$1.csr -CA ../ca/CA-cert.pem -CAkey ../ca/CA-key.pem -CAcreateserial -out ../ssl/$1-cert.pem
openssl x509 -req -days 365 -in ../ssl/$1.csr -CA ../ca/CA-cert.pem -CAkey ../ca/CA.key -CAcreateserial -out ../ssl/$1-cert.pem
rm ../ssl/$1.csr
