# Python3 Quick start example: embedded signing ceremony.
# Copyright (c) 2018 by DocuSign, Inc.
# License: The MIT License -- https://opensource.org/licenses/MIT

import base64, os, uuid, ds_config, config
from flask import Flask, request, redirect, render_template, url_for, session, flash
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document, RecipientViewRequest
from flask_oauthlib.client import OAuth
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import requests
from PyPDF2 import PdfFileReader, PdfFileWriter

# Settings
# Fill in these constants
#
# Obtain an OAuth access token from https://developers.docusign.com/oauth-token-generator
access_token = ""

# Obtain your accountId from demo.docusign.com -- the account id is shown in the drop down on the
# upper right corner of the screen by your picture or the default picture. 
account_id = ds_config.DS_CONFIG['account_id']
# Recipient Information:
signer_name = ds_config.DS_CONFIG['signer_name']
signer_email = ds_config.DS_CONFIG['signer_email']
# The document you wish to send. Path is relative to the root directory of this repo.
file_name_path = 'demo_documents/World_Wide_Corp_lorem.pdf'
# The url of this web application
base_url = 'http://127.0.0.1:5000'
client_user_id = '420' # Used to indicate that the signer will use an embedded
                       # Signing Ceremony. Represents the signer's userId within
                       # your application.
authentication_method = 'None' # How is this application authenticating
                               # the signer? See the `authenticationMethod' definition
                               # https://developers.docusign.com/esign-rest-api/reference/Envelopes/EnvelopeViews/createRecipient

# The API base_path
base_path = 'https://demo.docusign.net/restapi'

# Set FLASK_ENV to development if it is not already set
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'development'

# Constants
APP_PATH = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
def url_for_self(**args):
    return url_for(request.endpoint, **dict(request.view_args, **args))


def add_sign_anchor(filename):
    output = PdfFileWriter()
    
    input1 = PdfFileReader(file(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb"))
    output.addPage(input1.getPage(0))
    outputStream = file(os.path.join(app.config['UPLOAD_FOLDER'], str(filename)+"_out"), "wb")
    output.write(outputStream)
    outputStream.close()

@app.route('/embedded_signing_ceremony', methods=['GET','POST'])
def embedded_signing_ceremony():
    """
    The document <file_name> will be signed by <signer_name> via an
    embedded signing ceremony.
    """
    if request.method == 'POST':
        if request.files['file_to_sign']:
            file = request.files['file_to_sign']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            add_sign_anchor(filename)

    if ds_token_ok():
        access_token = session['ds_access_token']
    else:
        # Save the current operation so it will be resumed after authentication
        session['eg'] = url_for_self()
        redirect_url = url_for('ds_login')
        return redirect(redirect_url, code=302)


    #
    # Step 1. The envelope definition is created.
    #         One signHere tab is added.
    #         The document path supplied is relative to the working directory
    #
    with open(os.path.join(APP_PATH, file_name_path), "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode('ascii')

    # Create the document model
    document = Document( # create the DocuSign document object 
        document_base64 = base64_file_content, 
        name = 'Example document', # can be different from actual file name
        file_extension = 'pdf', # many different document types are accepted
        document_id = 1 # a label used to reference the doc
    )

    # Create the signer recipient model 
    signer = Signer( # The signer
        email = signer_email, name = signer_name, recipient_id = "1", routing_order = "1",
        client_user_id = client_user_id, # Setting the client_user_id marks the signer as embedded
    )

    # Create a sign_here tab (field on the document)
    sign_here = SignHere( # DocuSign SignHere field/tab
        document_id = '1', page_number = '1', recipient_id = '1', tab_label = 'SignHereTab',
        x_position = '195', y_position = '147')

    # Add the tabs model (including the sign_here tab) to the signer
    signer.tabs = Tabs(sign_here_tabs = [sign_here]) # The Tabs object wants arrays of the different field/tab types

    # Next, create the top level envelope definition and populate it.
    envelope_definition = EnvelopeDefinition(
        email_subject = "Please sign this document sent from the Python SDK",
        documents = [document], # The order in the docs array determines the order in the envelope
        recipients = Recipients(signers = [signer]), # The Recipients object wants arrays for each recipient type
        status = "sent" # requests that the envelope be created and sent.
    )
    
    #
    #  Step 2. Create/send the envelope.
    #
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(account_id, envelope_definition=envelope_definition)

    #
    # Step 3. The envelope has been created.
    #         Request a Recipient View URL (the Signing Ceremony URL)
    #
    envelope_id = results.envelope_id
    recipient_view_request = RecipientViewRequest(
        authentication_method = authentication_method, client_user_id = client_user_id,
        recipient_id = '1', return_url = base_url + '/dsreturn',
        user_name = signer_name, email = signer_email
    )

    results = envelope_api.create_recipient_view(account_id, envelope_id,
        recipient_view_request = recipient_view_request)
    
    #
    # Step 4. The Recipient View URL (the Signing Ceremony URL) has been received.
    #         Redirect the user's browser to it.
    #
    return redirect(results.url)


# Mainline

app.secret_key = ds_config.DS_CONFIG['session_secret']
base_uri_suffix = '/restapi'
oauth = OAuth(app)
request_token_params = {'scope': 'signature',
                        'state': lambda: uuid.uuid4().hex.upper()}
if not ds_config.DS_CONFIG['allow_silent_authentication']:
    request_token_params['prompt'] = 'login'
docusign = oauth.remote_app(
    'docusign',
    consumer_key=ds_config.DS_CONFIG['ds_client_id'],
    consumer_secret=ds_config.DS_CONFIG['ds_client_secret'],
    access_token_url=ds_config.DS_CONFIG['authorization_server'] + '/oauth/token',
    authorize_url=ds_config.DS_CONFIG['authorization_server'] + '/oauth/auth',
    request_token_params=request_token_params,
    base_url=None,
    request_token_url=None,
    access_token_method='POST'
)

@app.route('/login')
def ds_login():
    return docusign.authorize(callback=url_for('ds_callback', _external=True))




################################################################################
#
# OAuth support for DocuSign
#


def ds_token_ok(buffer_min=60):
    """
    :param buffer_min: buffer time needed in minutes
    :return: true iff the user has an access token that will be good for another buffer min
    """

    ok = 'ds_access_token' in session and 'ds_expiration' in session
    ok = ok and (session['ds_expiration'] - timedelta(minutes=buffer_min)) > datetime.utcnow()
    return ok





@app.route('/logout')
def ds_logout():
    ds_logout_internal()
    flash('You have logged out from DocuSign.')
    return redirect(url_for('homepage'))


def ds_logout_internal():
    # remove the keys and their values from the session
    session.pop('ds_access_token', None)
    session.pop('ds_refresh_token', None)
    session.pop('ds_user_email', None)
    session.pop('ds_user_name', None)
    session.pop('ds_expiration', None)
    session.pop('ds_account_id', None)
    session.pop('ds_account_name', None)
    session.pop('ds_base_path', None)
    session.pop('envelope_id', None)
    session.pop('eg', None)
    session.pop('envelope_documents', None)
    session.pop('template_id', None)


@app.route('/callback')
def ds_callback():
    """Called via a redirect from DocuSign authentication service """
    # Save the redirect eg if present
    redirect_url = session.pop('eg', None)
    # reset the session
    ds_logout_internal()

    resp = docusign.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    # app.logger.info('Authenticated with DocuSign.')
    flash('You have authenticated with DocuSign.')
    session['ds_access_token'] = resp['access_token']
    session['ds_refresh_token'] = resp['refresh_token']
    session['ds_expiration'] = datetime.utcnow() + timedelta(seconds=resp['expires_in'])

    # Determine user, account_id, base_url by calling OAuth::getUserInfo
    # See https://developers.docusign.com/esign-rest-api/guides/authentication/user-info-endpoints
    url = ds_config.DS_CONFIG['authorization_server'] + '/oauth/userinfo'
    auth = {"Authorization": "Bearer " + session['ds_access_token']}
    response = requests.get(url, headers=auth).json()
    session['ds_user_name'] = response["name"]
    session['ds_user_email'] = response["email"]
    accounts = response["accounts"]
    account = None # the account we want to use
    # Find the account...
    target_account_id = ds_config.DS_CONFIG['target_account_id']
    if target_account_id:
        account = next( (a for a in accounts if a["account_id"] == target_account_id), None)
        if not account:
            # Panic! The user does not have the targeted account. They should not log in!
            raise Exception("No access to target account")
    else: # get the default account
        account = next((a for a in accounts if a["is_default"]), None)
        if not account:
            # Panic! Every user should always have a default account
            raise Exception("No default account")

    # Save the account information
    session['ds_account_id'] = account["account_id"]
    session['ds_account_name'] = account["account_name"]
    session['ds_base_path'] = account["base_uri"] + base_uri_suffix

    if not redirect_url:
        redirect_url = url_for('homepage')
    return redirect(redirect_url)

################################################################################

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        return '''
        <html lang="en"><body><form action="{url}" method="post" enctype="multipart/form-data">
        <input type="file" accept=".pdf" name="file_to_sign"
                style="width:13em;height:2em;background:#1f32bb;color:white;font:bold 1.5em arial;margin: 3em;"/>
        <input type="submit" value="Sign the document!"
                style="width:13em;height:2em;background:#1f32bb;color:white;font:bold 1.5em arial;margin: 3em;"/>
        </form></body>
        '''.format(url=url_for('embedded_signing_ceremony'))
        # return redirect(url_for('embedded_signing_ceremony'), code=302)
    else:
        return '''
            <html lang="en"><body><form action="{url}" method="post" >
            <input type="submit" value="Sign the document!"
                style="width:13em;height:2em;background:#1f32bb;color:white;font:bold 1.5em arial;margin: 3em;"/>
            </form></body>
        '''.format(url=request.url)
@app.route('/dsreturn', methods=['GET'])
def dsreturn():
    return '''
        <html lang="en"><body><p>The signing ceremony was completed with
          status {event}</p>
          <p>This page can also implement post-signing processing.</p>
          <form action="{url}" method="get">
          <input type="submit" value="Back to homepage"
            style="width:13em;height:2em;background:#1f32bb;color:white;font:bold 1.5em arial;margin: 3em;"/>
          </form></body>
    '''.format(event=request.args.get('event'), url=url_for('homepage'))

app.run()
