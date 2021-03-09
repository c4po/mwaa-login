from flask import Flask, render_template, request
import datetime
import pytz
import boto3

app = Flask(__name__)

default_region="us-east-1"

sts_client = boto3.client("sts", region_name=default_region)

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    return value.strftime(format)

def getLoginUrl(account, environment):
    rolearn = "arn:aws:iam::" + account +":role/" + environment + "-devops-user"
    assumed_role_object=sts_client.assume_role(
        RoleArn=rolearn,
        RoleSessionName="AssumeRoleSession1"
    )
    credentials=assumed_role_object['Credentials']
    client=boto3.client(
        'mwaa', region_name=default_region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    response = client.create_web_login_token(
        Name=environment
    )

    url = "https://" + response["WebServerHostname"] + "/aws_mwaa/aws-console-sso?login=true#" + response["WebToken"]
    return url

@app.route("/")
def index():
    return render_template('home.html',
         title="Index", current_time=datetime.datetime.now(pytz.timezone("EST")))

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        environment = request.form.get('environment')
        account = request.form.get('account')
        url = getLoginUrl(account, environment)
    return render_template('mwaa.html',
        title="Index", url= url, environment= environment, account=account,
        current_time=datetime.datetime.now(pytz.timezone("EST")))

if __name__ == '__main__':
    app.run()
