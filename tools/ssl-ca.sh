#!/bin/bash
#
#
#
openssl genrsa -out ../ca/CA-key.pem 4096
openssl rsa -in ../ca/CA-key.pem -outform PEM -pubout -out ../ca/CA.pub
openssl req -new -subj "C=SE/O=RIMS/CN=rims-ca" -key ../ca/CA-key.pem -x509 -days 1825 -out ../ca/CA-cert.pem
openssl x509 -in ../ca/CA-cert.pem -outform der -out ../ca/CA-cert.crt
cp ../ca/CA-cert.crt ../site/CA-cert.crt
cp ../ca/CA-cert.crt ../static/CA-cert.crt
