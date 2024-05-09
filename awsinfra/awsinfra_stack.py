from aws_cdk import (
    # Duration,
    Stack,
     aws_ssm as ssm,
     aws_lambda as aws_lambda,
     aws_ec2 as ec2,
     aws_eks as eks,
     aws_iam as aws_iam,
     CustomResource as customresource,
     CustomResourceProvider,
     CustomResourceProviderRuntime
)
from constructs import Construct
from aws_cdk.lambda_layer_kubectl_v29 import KubectlV29Layer
import awsinfra.config as config
import aws_cdk as cdk
# Class to create Lambda function to get parameter values from Parameter Store
class AwsinfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Function to create Parameter store and store the value .
        ssm_fn = ssm.StringParameter(self, "Parameter",
                            allowed_pattern=".*",
                            description="Parameter Value",
                            parameter_name=config.ssm_parameter_name,
                            string_value=config.ssm_parameter_value,
                            )

        # Create Lambda Function that would fetch the Parameter store value SSM Parameter store
        lambda_get_param = aws_lambda.Function(self,"lambdagetssm",code=aws_lambda.Code.from_asset("lambda_source",
                                               bundling=cdk.BundlingOptions(
                                                  image=aws_lambda.Runtime.PYTHON_3_9.bundling_image,
                                                command=["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"],
                                                user="root",
                                                )),
                                               function_name=config.function_name,
                                               environment={
                                                   "param": config.ssm_parameter_name
                                               },
                                               handler="lambda_fn.lambda_handler",
                                               runtime=aws_lambda.Runtime.PYTHON_3_9,
                                               )
        # Grant Permission for Lambda to read from SSM
        ssm_fn.grant_read(lambda_get_param)

        # Create Custom Resource that invoke the above Lambda Function
        cr = customresource(self, "MyResource",
                            resource_type="Custom::MyCustomResourceType",
                            service_token=lambda_get_param.function_arn,
                            )
        self.replica_value = cr.get_att("param")


class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a basic VPC required for the EKs Cluster
        self.vpc = ec2.Vpc(self, "Vpc",
                      ip_addresses=ec2.IpAddresses.cidr(config.vpc_cidr),
                      nat_gateways=1,
                      vpc_name=config.vpc_name,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              name='Public-Subnet',
                              subnet_type=ec2.SubnetType.PUBLIC,
                              cidr_mask=24
                          ),
                          ec2.SubnetConfiguration(
                              name='Private-Subnet',
                              subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                              cidr_mask=24,
                          )]
                      )

class EksStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, replica_value: int, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new EKS Cluster in the VPC created above
        eks_new = eks.Cluster(self, "ekstest",
                 cluster_name=config.cluster_name,
                 version=eks.KubernetesVersion.V1_29,
                 vpc=vpc,
                 vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
                 default_capacity=2,
                default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
                            )
        # Deploy the Helm Chart and provide the value for replicaCount based on the Lambda Function Output
        eks.HelmChart(self, "helmchart",
                      cluster=eks_new,
                      chart=config.helm_chart_config["chart"],
                      repository=config.helm_chart_config["repo_url"],
                      namespace=config.helm_chart_config["namespace"],
                      version=config.helm_chart_config["chart_version"],
                      values={
                          "controller": {
                              "replicaCount": replica_value,
                          }
                      })

        # Add users that require masters role or access to the EKS Cluster            )
        for user in config.user_list:
          add_eks_master = aws_iam.User.from_user_name(self,f"Myuser={user}", user_name=user)
          eks_new.aws_auth.add_user_mapping(add_eks_master, groups=["system:masters"])
