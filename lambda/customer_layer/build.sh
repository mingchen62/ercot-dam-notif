#!/bin/bash


export PKG_DIR="python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}
docker run --rm -v $(pwd):/pkg_dir -w /pkg_dir lambci/lambda:build-python3.8 \
    pip install -r requirements.txt -t ${PKG_DIR}/lib/python3.8/site-packages
pkg_name="ercot-dam-notif-lambda-layer.zip" 
echo "${pkg_name}"
zip -r "${pkg_name}" python
unzip -l "${pkg_name}"
#rm -rf ${PKG_DIR}