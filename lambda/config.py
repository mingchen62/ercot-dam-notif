import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB Configuration
TABLE_NAME_DEFAULT = "ERCOT-DAM-Notif"

# 3 years of data retention in seconds
TABLE_TTL_DEFAULT = 3600*24*365*3
ISO_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

# DynamoDB table fields 
DT_COLUMN = 'dt'
DAILY_CURTAIL_HRS_COLUMN = 'daily_curtail_hrs'
DAILY_RUNNING_AVG_COLUMN = 'daily_running_avg'

MONTHLY_CURTAIL_HRS_COLUMN = 'monthly_curtail_hrs'
MONTHLY_RUNNING_AVG_COLUMN = 'monthly_running_avg'
MONTHLY_AVG_COLUMN = 'monthly_avg'
YEARLY_CURTAIL_HRS_COLUMN = 'yearly_curtail_hrs'
YEARLY_RUNNING_AVG_COLUMN = 'yearly_running_avg'

DAM_DATA_COLUMN = "dam_data"
INSERTION_TS_COLUMN = "insertion_ts"
EXPIRATION_TS_COLUMN = 'expiration_time'

DT_FORMAT = '%m/%d/%Y'