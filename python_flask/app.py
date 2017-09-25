import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os

from flask import Flask, jsonify, request, render_template


app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(("AWS4" + key).encode("utf-8"), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "aws4_request")
    return kSigning


@app.route("/signing", methods=['POST'])
def signing():

    bucket = os.environ['BUCKET']
    region = os.environ['REGION']
    data = request.json
    keyStart = data['name']
    acl = 'private'
    accessKeyId = os.environ['AWS_ACCESS_KEY_ID']
    secretAccessKey = os.environ['AWS_SECRET_ACCESS_KEY']
    dateString = datetime.now().strftime("%Y%m%d")
    credential = '/'.join([accessKeyId, dateString, region, 's3/aws4_request'])
    xAmzDate = dateString + 'T000000Z'

    # Build policy.
    dict = {
        # 1 minutes into the future
        'expiration': (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        'conditions': [
            {'bucket': bucket},
            {'acl': acl},
            {'x-amz-algorithm': 'AWS4-HMAC-SHA256'},
            {'x-amz-credential': credential},
            {'x-amz-date': xAmzDate},
            ['starts-with', '$key', keyStart],
        ],
    }

    # Generate signature.
    policyDocument = json.dumps(dict)
    policyBase64 = base64.b64encode(policyDocument.encode('utf-8'))
    signature_key = getSignatureKey(secretAccessKey, dateString, region, 's3')
    signature = hmac.new(signature_key, policyBase64, hashlib.sha256).hexdigest()

    res = {
        "url": 'https://s3-%s.amazonaws.com/%s' % (region, bucket),
        'bucket': bucket,
        'region': region,
        'keyStart': keyStart,
        'form': {
            'key': keyStart,
            'acl': acl,
            'policy': policyBase64.decode('utf-8'),
            'x-amz-algorithm': 'AWS4-HMAC-SHA256',
            'x-amz-credential': credential,
            'x-amz-date': xAmzDate,
            'x-amz-signature': signature
        }
    }
    return jsonify(res)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
