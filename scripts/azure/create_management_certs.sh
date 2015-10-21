#! /bin/bash
#pass=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w10 | head -n1)
#echo $pass
pass=launcherKeystore
datestr=$(date +%Y%m%d%H%M%S)

echo "generate keypair"
keytool -genkey -alias launcher_keystore \
        -keystore ~/.keystore/launcher.pfx \
        -storepass "$pass" \
        -keypass "$pass" \
        -storetype pkcs12 \
        -validity 3650 \
        -keyalg RSA \
        -keysize 2048 \
        -dname "cn=Self Signed Certificate $datestr, ou=Launcher, o=Launcher, L=AzureCloud, S=NA, C=US"

echo "generate cert"
keytool -export -alias launcher_keystore \
        -storetype pkcs12 \
        -keystore ~/.keystore/launcher.pfx \
        -storepass $pass \
        -rfc \
        -file ~/.keystore/launcher.cert

echo "Now you have to manually upload ~/.keystore/launcher_key.cert to the classic Azure portal."

echo "generating jks file"
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

