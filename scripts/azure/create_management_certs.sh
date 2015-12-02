#! /bin/bash

pass=launcherKeystore
datestr=$(date +%Y%m%d%H%M%S)

# create the directory if it doesn't exist.
if [ ! -d ~/.keystore ] ; then
    mkdir ~/.keystore
fi

echo "Now generating keypair..."
keytool -genkey -alias launcher_keystore \
        -keystore ~/.keystore/launcher.pfx \
        -storepass "$pass" \
        -keypass "$pass" \
        -storetype pkcs12 \
        -validity 3650 \
        -keyalg RSA \
        -keysize 2048 \
        -dname "cn=Self Signed Certificate $datestr, ou=Launcher, o=Launcher, L=AzureCloud, S=NA, C=US"

echo "Now generating certificate file..."
keytool -export -alias launcher_keystore \
        -storetype pkcs12 \
        -keystore ~/.keystore/launcher.pfx \
        -storepass $pass \
        -rfc \
        -file ~/.keystore/launcher.cer

echo "Now you have to manually upload ~/.keystore/launcher.cer to the classic Azure portal."

echo "Now generating Java KeyStore..."
keytool -importkeystore \
        -srckeystore ~/.keystore/launcher.pfx \
        -destkeystore ~/.keystore/launcher.jks \
        -srcstoretype pkcs12 \
        -deststoretype JKS \
        -srcstorepass $pass \
        -deststorepass $pass \
        -srckeypass $pass \
        -destkeypass $pass \
        -alias launcher_keystore

echo "The JKS file has now been created at ~/.keystore/launcher.jks You can now reference it in ~/.youxia/config"

