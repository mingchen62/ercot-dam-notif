import json
from bs4 import BeautifulSoup
import urllib.request as req
import ssl
import logging
import pandas as pd

from send_email import send_email_via_ses, dictionaryToHTMLTable, listToHTMLTable, SUPPORT, RECIPIENT
from db_helper import update_table

logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = 'https://www.ercot.com/content/cdr/html/dam_spp.html'
#url= 'https://www.ercot.com/content/cdr/html/20220301_dam_spp.html'

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
headers = {'User-Agent':user_agent,}
gcontext = ssl.SSLContext()
curtail_threshold = 80
avg_threshold = 35


def lambda_handler(event, context):
    
    # retrieve Ercot DAM data
    try:
        request = req.Request(url,None,headers)
        response = req.urlopen(request, timeout = 100, context=gcontext)
        soup = BeautifulSoup(response.read(), 'html.parser', from_encoding="iso-8859-1")
        table = soup.find('table')

    except Exception as e:
        logger.error('Error in retrieving ercot info', exc_info=e)
        send_email_via_ses(SUPPORT, 'Error in retrieving ercot info', 'Error in retrieving ercot info' )   

        return {
        'statusCode': 500,
        'body': json.dumps('Error in retrieving ercot info')
    }
    
    if table is None:
        send_email_via_ses(SUPPORT, 'Empty ercot DAM table', 'Empty ercot DAM table' )   

        return {
        'statusCode': 500,
        'body': json.dumps('Empty ercot DAM table')
        }

    # data preprocessing
    try:
        table_headers = []
        for tx in soup.find_all('th'):
            table_headers.append(tx.get_text())
        output_rows = []
        for table_row in table.findAll('tr'):
            columns = table_row.findAll('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            if output_row:
                output_rows.append(output_row)
    except Exception as e:
        logger.error('Error in processing ercot info', exc_info=e)
        send_email_via_ses(SUPPORT, 'Error in processing ercot info', 'Error in processing ercot info' )   

        return {
        'statusCode': 500,
        'body': json.dumps('Error in processing ercot info')
        }
            
    df = pd.DataFrame(output_rows, columns=table_headers)     
    df['HB_NORTH']=df['HB_NORTH'].astype(float)
    df['Hour Ending']=df['Hour Ending'].astype(int)
    df['Hour']=  df['Hour Ending'].apply(lambda x: f"{x-1}:01-{x}:00")

    df = df[['Oper Day','Hour Ending', 'Hour','HB_NORTH']]

    df['Curtail'] = df.apply(lambda row: 'Y' if row['HB_NORTH'] >=curtail_threshold  and df["HB_NORTH"].mean() >= avg_threshold  else 'N',
                     axis=1)

    total_hours_curtailed = 0
    sum_electricity_running = 0
    sum_electricity = 0
    for i, row in df.iterrows():
        oper_day = row['Oper Day']
        sum_electricity += row['HB_NORTH']
        if row['Curtail'] == 'Y':
            total_hours_curtailed += 1
        else:
            sum_electricity_running += row['HB_NORTH']
    
    avg_electricity = sum_electricity_running/24
    avg_electricity_running = sum_electricity_running/(24-total_hours_curtailed)
    #html_table = dictionaryToHTMLTable(df.to_dict(orient='list'))
 
    monthly_running_avg, monthly_uptime, yearly_running_avg, yearly_uptime = update_table(oper_day, avg_electricity_running, total_hours_curtailed, df.to_dict(orient='list'))

    sla_header = ['Metric','Value']
    sla_list =[
        ["Yearly uptime", "{:.1%}".format(yearly_uptime)],
        ["Yearly running average", "{:.2f}".format(yearly_running_avg)],
        ["Monthly uptime", "{:.1%}".format(monthly_uptime)],
        [ "Monthly running average", "{:.2f}".format(monthly_running_avg)],
        ["Daily running average", "{:.2f}".format(avg_electricity_running)],
        ["Daily Hours curtailed", str(total_hours_curtailed)]
    ]
    curtail_header = ['Hour Ending','Hour', 'HB_NORTH','Curtail']
    curtail_list = df[curtail_header].values.tolist()

    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Aloha Innoblock!</h1>
      <p>
      <h4>SLA Metrics</h4>
      {listToHTMLTable(sla_list, sla_header)}
      <p>
      <h4>{oper_day} Curtailment Schedule</h4>
      <p>
      {listToHTMLTable(curtail_list, curtail_header)}
      </p>
    </body>
    </html>
    """ 
    send_email_via_ses(RECIPIENT,   oper_day+ " Total Hours to curtail: "+str(total_hours_curtailed), body_html )   
    return {
        'statusCode': 200,
        'body': json.dumps({'Hours to be curtailed [0-24]': str(df['Curtail'])})
    }
