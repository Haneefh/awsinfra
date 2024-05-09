#!/usr/bin/env python3
import os

import aws_cdk as cdk

from awsinfra.awsinfra_stack import AwsinfraStack
from awsinfra.awsinfra_stack import EksStack
from awsinfra.awsinfra_stack import NetworkStack

app = cdk.App()

network_stack = NetworkStack(app, "NetworkStack")
awsinfra_stack = AwsinfraStack(app, "AwsinfraStack")
EksStack(app, "EksStack", network_stack.vpc,awsinfra_stack.replica_value)

app.synth()
