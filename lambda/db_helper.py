import boto3
import botocore
import logging
import os
import time
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone
from decimal import Decimal
import json

from datetime import datetime
from datetime import timedelta

from config import (
    DT_COLUMN,
    DAILY_CURTAIL_HRS_COLUMN,
    DAILY_RUNNING_AVG_COLUMN,

    MONTHLY_CURTAIL_HRS_COLUMN,
    MONTHLY_RUNNING_AVG_COLUMN,
    MONTHLY_AVG_COLUMN,

    YEARLY_CURTAIL_HRS_COLUMN,
    YEARLY_RUNNING_AVG_COLUMN,
    DAM_DATA_COLUMN,
    INSERTION_TS_COLUMN,
    EXPIRATION_TS_COLUMN,
    TABLE_NAME_DEFAULT,
    TABLE_TTL_DEFAULT,
    ISO_FORMAT,
    DT_FORMAT)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# dynamo db config and initialization
dynamodb = boto3.resource('dynamodb')

table_name = os.environ.get('TABLENAME_OVERRIDE', TABLE_NAME_DEFAULT)
logger.info("table_name %s", table_name)

try:
    TABLE_TTL = int(os.environ.get('TABLE_TTL', TABLE_TTL_DEFAULT))
except:
    TABLE_TTL = TABLE_TTL_DEFAULT
logger.info("TABLE_TTL %d", TABLE_TTL)

try:
    table = dynamodb.Table(table_name)
except Exception as e:
    logger.error(
            'Error in connecting to dynamob table {}, Skipping execution.'.format(table_name),
            exc_info=e)
    exit(1)

def _query(dt):
    # DB query
    response = table.query(
            KeyConditionExpression=Key(DT_COLUMN).eq(dt)
        )

    if len(response['Items']) >0 :
        return response['Items'][0]
    else:
        return None

def _insert(item):
    # Add timestamps
    item[INSERTION_TS_COLUMN]= datetime.fromtimestamp(datetime.timestamp(datetime.now()), tz=timezone.utc).strftime(ISO_FORMAT)
    item[EXPIRATION_TS_COLUMN]=  str(int(time.time() + TABLE_TTL))
    
    item = json.loads(json.dumps(item), parse_float=Decimal)

    # DB insertion
    table.put_item(
            Item=item
        )
    logger.debug('PutItem succeeded %s', str(item))

def hours_in_the_month(open_day):
    d= datetime.strptime(open_day, DT_FORMAT)
    dif_month = d- d.replace(day=1)
    return (dif_month.days+1)*24

def hours_in_the_year(open_day):
    d= datetime.strptime(open_day, DT_FORMAT)
    dif_year =  d- d.replace(day=1, month =1)
    return (dif_year.days+1)*24

def get_monthly_metrics(d):
    print(d, d.day)
    if d.day == 1: # start from scratch if first day of the month
        return 0,0.0, 0.0
        
    yesterday = datetime.strftime(d - timedelta(days = 1), DT_FORMAT)
    item = _query(yesterday)
    return item[MONTHLY_CURTAIL_HRS_COLUMN], item[MONTHLY_RUNNING_AVG_COLUMN], item[MONTHLY_AVG_COLUMN]

def get_yearly_metrics(d):
    if d.day == 1  and d.month == 1: # start from scratch  if first day of the year
        return 0,0.0
        
    yesterday = datetime.strftime(d - timedelta(days = 1), DT_FORMAT)
    item = _query(yesterday)
    return item[YEARLY_CURTAIL_HRS_COLUMN], item[YEARLY_RUNNING_AVG_COLUMN]

def update_table(oper_day, daily_avg, daily_running_avg, daily_hours_curtailed, dam_data):
    #print("oper day", oper_day)
    d = datetime.strptime(oper_day, DT_FORMAT)

    monthly_curtail_hrs,monthly_running_avg, monthly_avg  = get_monthly_metrics(d)

    # Calculate new metrics up to open_day

    monthly_running_hours_prev = int(hours_in_the_month(oper_day)- monthly_curtail_hrs-24) # excluding open_day
    monthly_running_sum_prev = monthly_running_hours_prev *monthly_running_avg
    monthly_running_sum = float(monthly_running_sum_prev) + (24-daily_hours_curtailed) *daily_running_avg 
    monthly_running_avg =  monthly_running_sum/(monthly_running_hours_prev +24-daily_hours_curtailed)
    monthly_sum_prev = (hours_in_the_month(oper_day) -24) *float(monthly_avg)

    monthly_avg =  (monthly_sum_prev+24*daily_avg)/float(hours_in_the_month(oper_day))

    monthly_curtail_hrs = monthly_curtail_hrs + daily_hours_curtailed
    monthly_uptime = 1- float(monthly_curtail_hrs)/hours_in_the_month(oper_day)

  
    # store
    item = {
        DT_COLUMN:oper_day,
        DAILY_CURTAIL_HRS_COLUMN: int(daily_hours_curtailed),
        DAILY_RUNNING_AVG_COLUMN: float(daily_running_avg),
        MONTHLY_CURTAIL_HRS_COLUMN: int(monthly_curtail_hrs),
        MONTHLY_RUNNING_AVG_COLUMN: float(monthly_running_avg),
        MONTHLY_AVG_COLUMN: float(monthly_avg),
        DAM_DATA_COLUMN: dam_data
    
    }
    #print(item)
    _insert(item)
    return monthly_curtail_hrs, monthly_running_avg, monthly_avg