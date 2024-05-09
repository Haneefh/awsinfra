import json
import requests
import boto3
import os

# Function to get the string value from Parameter and convert it into an integer based on the value
"""
  If the string value is development , function should generate an int value of 1 in the body
  If the string value is production or staging, function should generate an int value of 2 in the body
"""
def get_param(name):
    responseData = {}
    try:
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=name
        )
        output = (response["Parameter"]["Value"])
        if output.lower() == "staging":
          responseData = {'Success': 'Test Passed.', 'param': 2}
        elif output.lower() == "production":
          responseData = {'Success': 'Test Passed.', 'param': 2}
        elif output.lower() == "development":
          responseData = {'Success': 'Test Passed.', 'param': 1}
        else:
          responseData = {'Success': 'Test Passed.', 'param': "Wrong value in Parameter store"}
        print(responseData)
        return(responseData)
    except:
        return responseData

def lambda_handler(event, context):
    responseStatus = 'SUCCESS'
    responseData = {}
    if event['RequestType'] == 'Create':
        try:
          responseData = get_param(os.environ['param'])
          sendResponse(event, context, responseStatus, responseData)
        except:
            sendResponse(event, context, responseStatus, responseData)
    else:
        responseData = {'Success': 'Test Passed.'}
        sendResponse(event, context, responseStatus, responseData)

"""
The Lambda Function is invoked by a Custom Resource , Cloud Formation sends a response URL to which it expects a response fro the Lambda Funcction
and hence we have the below Function
"""
def sendResponse(event, context, responseStatus, responseData):
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    print('RESPONSE BODY:n' + json.dumps(responseBody))
    try:
        req = requests.put(event['ResponseURL'], data=json.dumps(responseBody))
        if req.status_code != 200:
            print(req.text)
            raise Exception('Received non 200 response while sending response to CFN.')
        return
    except requests.exceptions.RequestException as e:
        print(e)
        raise
