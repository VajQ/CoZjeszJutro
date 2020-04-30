from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from python_http_client.exceptions import HTTPError


def district_switch(district):
    districts = {
        1: 'Bemowo',
        2: 'Białołęka',
        3: 'Bielany',
        4: 'Mokotów',
        5: 'Ochota',
        6: 'Praga-Południe',
        7: 'Praga-Północ',
        8: 'Rembertów',
        9: 'Śródmieście',
        10: 'Targówek',
        11: 'Ursus',
        12: 'Ursynów',
        13: 'Wawer',
        14: 'Wesoła',
        15: 'Wilanów',
        16: 'Włochy',
        17: 'Wola',
        18: 'Żoliborz'
    }
    return districts.get(district)




def send_email(to, subject, content):
    email = Mail(from_email='noreply@cjno.com', to_emails=to)
    email.add_content(Content("text/plain", content))
    email.subject = subject
     
    sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
   
    try:
        response = sg.send(email)        
    except HTTPError as e:
        print(e.to_dict)