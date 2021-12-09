#!/bin/bash
#set -x
rm -rf "./target" || true
mkdir "./target"

if [ "$#" -ne 1 ] ; then
  echo "Usage: $0 <s3 bucket>" >&2
  echo "Please specify a s3 bucket which you have write access and S3 versioning is enabled"
  exit 1
fi

s3_bucket=$1

aws_profile=lanking

## package lambda and upload 
cd ./lambda; zip "../target/ercot-dam-notif-lambda.zip" *.py; cd ../
# copy lambda artifact to s3 bucket and get its s3 version
ercot_dam_notif_lambda_s3_version=$(aws s3api put-object --bucket ${s3_bucket} --body ./target/ercot-dam-notif-lambda.zip --key ercot-dam-notif-lambda.zip | jq -j '.VersionId')

## package lambda layer and upload
cd ./lambda/customer_layer; ./build.sh; cp ./ercot-dam-notif-lambda-layer.zip ../../target/; cd ../../
# copy lambda layer artifactto s3 bucket and get its s3 version
ercot_dam_notif_lambda_layer_s3_version=$(aws s3api put-object --bucket ${s3_bucket} --body ./target/ercot-dam-notif-lambda-layer.zip --key ercot-dam-notif-lambda-layer.zip  | jq -j '.VersionId')

echo "ercot_dam_notif_lambda_s3_version ${ercot_dam_notif_lambda_s3_version}"
echo "ercot_dam_notif_lambda_layer_s3_version ${ercot_dam_notif_lambda_layer_s3_version}"



