
# An AWS CDK Project to setup EKS Cluster and Install an application using Helm Chart
Setting up the environment to run the project
```
$ python -m venv .venv
```
After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:
```
% .venv\Scripts\activate.bat
```
Once the virtualenv is activated, you can install the required dependencies.
```
$ pip install -r requirements.txt
```
At this point you can now synthesize the CloudFormation template for this code.
```
$ cdk synth
```

## Description :
The project achieves the below . Its divided into three CDK Stacks
### AwsinfraStack
1. Creates an SSM Paramter store and stores a string value "development", "production" or "staging" based on the configuration user provides.
2. Creates a Lambda function and a custom resource which invokes the lambda Function. The Lambda function reads the parameter string value and stores it which is required in the following setup.

### Network Stack
1. Creates the VPC with a Public and Private Subnets .Also sets up Internet gateway and a Nat gateway.

### EksStack
1. Creates an EKS Cluster in the VPC sdetup using Network Stack.
2. Sets up Helm chart and uses the value retrieved by the Lambda function to pass onto the Helm Chart Value for "controller.replicaCount"

## Testing
A test using pytest is written to test the functionality of Lambda function and it can be executed as below

```
  pytest
```
### Note -
__The Lambda function built using aws cdk requires docker installed on the machine executing cdk as docker is used  to build 
zip the external dependencies required for the Lambda Function__

Usage
```
  cdk synth --all
  cdk deploy *
```
