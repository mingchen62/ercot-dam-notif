# Ercot-dam-notif

AWS stack to retrieve ERCOT DAM (Day-Ahead Market) and send notification

This stack utilize AWS lambda, dynamodb and SES to retrieve ERCOT DAM and send email notification.

## Data
https://www.ercot.com/content/cdr/html/20211209_dam_spp.html
DAM Settlement Point Prices

The display contains an hourly breakdown of the Settlement Point Prices for the Day-Ahead Market (DAM). The data provided is the available Settlement Point Prices for all Trading Hubs and Load Zones for the DAM operating day (if on or after 14:00).

The data provides the hourly market price for the DAM operating day as well as links to values for the past 6 days. The browser refreshes every hour. The data is updated daily after the DAM run.

## Prerequisites

Set up AWS account so we can deploy the above resources.

One S3 bucket with write access so we can upload artifacts. S3 versioing shall be enabled for the s3 bucket.

## Configuration
Configure email address in AWS SES

https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-email-set-up.html

Once sender/reciepent email addresses are verified in AWS SES, you can specify them in cloud formation:

RECEPIENTEMAILADDRESS, SENDEMAILADDRESS

## Package and deploy

Package lambda and lambda layer and upload to a S3 bucket. It will output S3 version of artifacts once those artifacts are uploaded.

$ ./package_deploy.sh

    deploy cloud formation stack.

You can deploy vis cloud formation console or use the follwoing command:

$ aws cloudformation deploy --template ./ercot-dam-notif-lambda.cfn.yml --stack-name ercot-dam-notif-stack
--parameter-overrides \
SharedBucketName=< s3 artifact bucket> \
ErcotDAMNotifLambdaArtifactS3Version=<> \
ErcotDAMNotifLambdaLayerArtifactS3Version=<>