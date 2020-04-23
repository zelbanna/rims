#!/bin/bash

openssl genrsa -aes256 -out ../CA-key.pem 4096
openssl rsa -in ../CA-key.pem -outform PEM -pubout -out ../CA.pub
openssl req -new -key ../CA-key.pem -x509 -days 1825 -out ../CA-cert.pem
openssl x509 -outform der -in ../CA-cert.pem -out ../CA-cert.crt
cp ../CA-cert.crt ../build/CA-cert.crt
cp ../CA-cert.crt ../public/CA-cert.crt

