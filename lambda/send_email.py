import boto3
from botocore.exceptions import ClientError
import logging

# Create a new SES resource
client = boto3.client('ses')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHARSET = "UTF-8"
RECIPIENT = "ming@innoblock.us"
SENDER = "ming@innoblock.us"
SUPPORT = "ming@innoblock.us"

class HTML:

    def __init__(self, Header, tableStyles = {}, trStyles = {}, thStyles = {}):
        self.tableStyles = HTML._styleConverter(tableStyles)
        trStyles = HTML._styleConverter(trStyles)
        thStyles = HTML._styleConverter(thStyles)
        self.rows = []
        self.Header= f'<tr {trStyles} >'
        for th in Header:
            self.Header += f'\n<th {thStyles} >{th}</th>'
        self.Header += '\n</tr>'

    @staticmethod
    def _styleConverter(styleDict : dict):
        if styleDict == {}:
            return ''
        styles = ''
        for [style, value] in styleDict.items():
            styles +=f'{style}: {value};'
        return f'style="{styles}"'

    def addRow(self, row, trStyles = {}, tdStyles = {}):
        trStyles = HTML._styleConverter(trStyles)
        tdStyles = HTML._styleConverter(tdStyles)
        temp_row = f'\n<tr {trStyles} >'
        for td in row:
            temp_row += f'\n<td {tdStyles} >{td}</td>'
        temp_row += '\n</tr>'
        self.rows.append(temp_row)


    def __str__(self):


        return \
f'''
<table {self.tableStyles} >
{self.Header}
{''.join(self.rows)}
</table>
'''

def dictionaryToHTMLTable( d):
    html = HTML(Header = d.keys(),
                tableStyles={'margin': '2px'},
                trStyles={'background-color': '#7cc3a97d'})
    for i, row in enumerate(zip(*d.values())):
        # last column is status. if status new, use a different color.
        if row[-1] == 'N':
            BGC = 'Lightgreen'
        else:
            BGC = 'red'
        html.addRow(row, trStyles={'background-color' : BGC}, tdStyles={'padding': '1rem'})
    return html
    
def send_email_via_ses(send_to_email, subject, body_html):
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    send_to_email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': "",
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,

        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        logger.error(e.response['Error']['Message'], exc_info=e)
    else:
        logger.info("Email sent! Message ID:"),
        logger.info(response['MessageId'])