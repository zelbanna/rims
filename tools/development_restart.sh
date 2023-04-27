#!/bin/bash
#
# Redirect all libs
#
SRCDIR=/usr/local/sbin/rims
PKGDIR=/usr/local/sbin/rims-frontend
rm -fR $PKGDIR/src;    mkdir $PKGDIR/src;    mount -B $SRCDIR/react $PKGDIR/src
rm -fR $PKGDIR/build;  mkdir $PKGDIR/build;  mount -B $SRCDIR/site  $PKGDIR/build
rm -fR $PKGDIR/public; mkdir $PKGDIR/public; mount -B $SRCDIR/static $PKGDIR/public
