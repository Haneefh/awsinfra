import pytest
import os
from moto import mock_aws
import boto3
import awsinfra.lambda_source.lambda_fn as fn

@pytest.fixture(scope='function')
def aws_credentials():
    os.environ['AWS_ACCESS_KEY_ID'] = "test"
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_SECURITY_TOKEN'] = 'test'
    os.environ['AWS_SESSION_TOKEN'] = 'test'


@mock_aws()
def test_get_paramS_staging(aws_credentials):
    conn = boto3.client("ssm")
    conn.put_parameter(Name='parameter_store',Value="staging", Type="String")
    # Invoke the Lambda function
    response = fn.get_param("parameter_store")
    assert response == {'Success': 'Test Passed.', 'param': 2}

@mock_aws()
def test_get_param_production(aws_credentials):
    conn = boto3.client("ssm")
    conn.put_parameter(Name='parameter_store',Value="production", Type="String")
    # Invoke the Lambda function
    response = fn.get_param("parameter_store")
    print(response)
    assert response == {'Success': 'Test Passed.', 'param': 2}


@mock_aws()
def test_get_param_development(aws_credentials):
    conn = boto3.client("ssm")
    conn.put_parameter(Name='parameter_store',Value="development", Type="String")
    # Invoke the Lambda function
    response = fn.get_param("parameter_store")
    assert response == {'Success': 'Test Passed.', 'param': 1}

@mock_aws()
def test_get_param_wrong(aws_credentials):
    conn = boto3.client("ssm")
    conn.put_parameter(Name='parameter_store',Value="qa", Type="String")
    # Invoke the Lambda function
    response = fn.get_param("parameter_store")
    assert response == {'Success': 'Test Passed.', 'param': "Wrong value in Parameter store"}
