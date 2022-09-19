terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.4"
    }
  }
  # We define a backend for the terraform state file. This saves all the changes related to the AWS elements.
  backend "s3" {
    bucket = "housing-api"
    key    = "statefile"
    region = "us-west-2"
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = "us-west-2"
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.example.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.example.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1alpha1"
    args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.example.name]
    command     = "aws"
  }
}

data "aws_eks_cluster" "example" {
  name = "my-cluster"
}

data "aws_eks_cluster_auth" "cluster-auth" {
  name = data.aws_eks_cluster.example.name
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.example.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.example.certificate_authority[0].data)
    #exec {
    #api_version = "client.authentication.k8s.io/v1beta1"
    #args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.example.name]
    # command     = "aws"
    #}
    token            = data.aws_eks_cluster_auth.cluster-auth.token
    load_config_file = false
  }
}

resource "helm_release" "housing-api-remote-release" {
  name         = "housing-api-release"
  chart        = "./housing-api"
  reset_values = true
  set {
    name  = "current-time"
    value = timestamp()
  }
}