from flask import Flask
from oauth2client import client
import requests, json, os, sys

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def main(request):
    
    ## Get environ variables
    base_url = os.environ['BASE_URL']
    audience = os.environ['AUDIENCE']
    token = os.environ['TOKEN']
    
    ## Get request message
    event = request.get_json()
    event_headers = dict(request.headers)
    
    # Verify message is authentic
    CHAT_ISSUER = 'chat@system.gserviceaccount.com'
    PUBLIC_CERT_URL_PREFIX = 'https://www.googleapis.com/service_accounts/v1/metadata/x509/'
    AUDIENCE = audience
    BEARER_TOKEN = event_headers['Authorization'][7:]
    try:
        token = client.verify_id_token(
        BEARER_TOKEN, AUDIENCE, cert_uri=PUBLIC_CERT_URL_PREFIX + CHAT_ISSUER)
        if token['iss'] != CHAT_ISSUER:
            sys.exit('Invalid issuee')
    except:
        sys.exit('Invalid token')
    
    ## Handle event from Google Chat
    user = event['message']['sender']['name']
    try:
        if event['message']['annotations']:
            if event['message']['annotations'][0]['type'] == 'SLASH_COMMAND' and event['message']['slashCommand']['commandId'] == "1":
                ticket_description = event['message']['argumentText']
                user_email = event['message']['sender']['email']
    except KeyError:
        return json.dumps({'text': f'Hello {user}, please use an available slash command.'})
                

    ## Create and send payload to IIQ
    url = f'{base_url}/api/v1.0/tickets/simple/new'
    
    headers = {
        'Client': 'ApiClient',
        'SiteId': 'b8b53b6e-d4a1-4173-a828-6715e6166871',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = json.dumps({
        'ForUsername': user_email,
        'Issue': 'Issue not listed > Issue not listed',
        'IssueDescription': ticket_description
    })
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.dumps({'text': f'Ticket has been created for {user}.'})

if __name__ == '__main__':
    app.run(port=8080, debug=True)