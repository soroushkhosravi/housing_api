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
  #exec {
  #api_version = "client.authentication.k8s.io/v1beta1"
  #args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.example.name]
  #command     = "aws"
  #}
  token = data.aws_eks_cluster_auth.cluster-auth.token
}

data "aws_eks_cluster" "example" {
  name = "my-cluster"
}

data "aws_eks_cluster_auth" "cluster-auth" {
  name = data.aws_eks_cluster.example.name
}

data "aws_cloudformation_stack" "my-eks-vpc-stack" {
  name = "my-eks-vpc-stack"
}

# We create a subnet group including all the public subnets of the VPC we created.
resource "aws_db_subnet_group" "first" {
  name       = "first"
  subnet_ids = slice(split(",", data.aws_cloudformation_stack.my-eks-vpc-stack.outputs.SubnetIds), 0, 2)
}

resource "random_password" "password" {
  length           = 16
  special          = true
  override_special = "!#$&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "secret" {
  name        = "/production/database/password/master"
  description = "The password for the production database."
  type        = "SecureString"
  value       = random_password.password.result

  tags = {
    environment = "production"
  }
}

resource "aws_security_group" "_" {
  name        = "first-sg"
  vpc_id      = data.aws_cloudformation_stack.my-eks-vpc-stack.outputs.VpcId
  description = "RDS (terraform-managed)"

  # Only MySQL in
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [data.aws_eks_cluster.example.vpc_config[0].cluster_security_group_id]
  }

  # Allow all outbound traffic.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "first" {
  identifier           = "first"
  allocated_storage    = 10
  db_subnet_group_name = aws_db_subnet_group.first.id
  engine               = "postgres"
  engine_version       = "12"
  instance_class       = "db.t2.small"
  db_name              = "firstsoroushdb"
  username             = "soroush"
  password             = random_password.password.result
  port                 = 5432
  publicly_accessible  = true
  skip_final_snapshot  = true

  vpc_security_group_ids = ["${aws_security_group._.id}"]
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.example.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.example.certificate_authority[0].data)
    #exec {
    #api_version = "client.authentication.k8s.io/v1beta1"
    #args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.example.name]
    #command     = "aws"
    #}
    token = data.aws_eks_cluster_auth.cluster-auth.token
  }
}

data "external" "env" {
  program = ["sh", "${path.module}/env.sh"]

  # For Windows (or Powershell core on MacOS and Linux),
  # run a Powershell script instead
  #program = ["${path.module}/env.ps1"]
}

resource "helm_release" "housing-api-remote-release" {
  name         = "housing-api-release"
  namespace    = "housing-api"
  chart        = "./housing-api"
  reset_values = true
  set {
    name  = "current-time"
    value = timestamp()
  }

  set {
    name  = "commit"
    value = data.external.env.result["CIRCLE_SHA1"]
  }

  set {
    name  = "db"
    value = aws_db_instance.first.endpoint
  }

  set {
    name  = "dbPassword"
    value = random_password.password.result
  }

  set {
    name  = "load-balancer-sg-id"
    value = aws_security_group.load-balancer-sg.id
  }
}

data "kubernetes_ingress_v1" "example" {
  metadata {
    name      = "housing-api-ingress"
    namespace = "housing-api"
  }
  depends_on = [helm_release.housing-api-remote-release]
}

data "aws_route53_zone" "selected" {
  name         = "housingselection.co.uk."
  private_zone = false
}

# Getting the elastic ip address of the private subnet to use for the security group pf the load balancer.
data "aws_eip" "private_subnet_1_elastic_ip" {
  filter {
    name   = "tag:Name"
    values = ["my-eks-vpc-stack-EIP1"]
  }
}

# Creating the security group for the load balancer.
resource "aws_security_group" "load-balancer-sg" {
  name        = "load-balancer-sg"
  vpc_id      = data.aws_cloudformation_stack.my-eks-vpc-stack.outputs.VpcId
  description = "Load Balancer (terraform-managed)"

  # Only MySQL in
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_eip.private_subnet_1_elastic_ip.public_ip]
  }

  # Allow all outbound traffic.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_route53_record" "abc" {
  name    = "test"
  type    = "CNAME"
  ttl     = 600
  zone_id = data.aws_route53_zone.selected.id

  records = [data.kubernetes_ingress_v1.example.status.0.load_balancer.0.ingress.0.hostname]
}