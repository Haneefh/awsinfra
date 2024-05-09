vpc_cidr = "10.0.0.0/16"
vpc_name = "eksvpc"
cluster_name = "cdk_cluster"
ssm_parameter_name = "/platform/account/env"
ssm_parameter_value = "staging"

helm_chart_config = {
    "chart": "ingress-nginx",
    "repo_url": "https://kubernetes.github.io/ingress-nginx",
    "namespace": "app",
    "chart_version": "4.10.0"
    }

function_name = "get_ssm"

# Eks Master users List
user_list = ["hharoon"]