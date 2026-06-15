terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "us-east-1"
}

##########################
# Terrible VPC Setup
##########################
resource "aws_vpc" "bad_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "bad-vpc"
  }
}

resource "aws_subnet" "bad_subnet" {
  vpc_id            = aws_vpc.bad_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "bad-subnet" }
}

resource "aws_internet_gateway" "bad_igw" {
  vpc_id = aws_vpc.bad_vpc.id
}

resource "aws_route_table" "bad_route" {
  vpc_id = aws_vpc.bad_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.bad_igw.id
  }
}

resource "aws_route_table_association" "bad_assoc" {
  subnet_id      = aws_subnet.bad_subnet.id
  route_table_id = aws_route_table.bad_route.id
}

##########################
# Terrible Security Group (WIDE OPEN)
##########################
resource "aws_security_group" "bad_sg" {
  name        = "bad-sg"
  description = "Open to the world"
  vpc_id      = aws_vpc.bad_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

##########################
# Single EC2 (Non-HA, small, expensive choice)
##########################
resource "aws_instance" "bad_ec2" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2 (hardcoded)
  instance_type = "t2.micro"             # Low performance
  subnet_id     = aws_subnet.bad_subnet.id
  security_groups = [aws_security_group.bad_sg.name]

  associate_public_ip_address = true

  tags = {
    Name = "bad-ec2"
  }
}

##########################
# RDS (Costly, Single AZ, no backups)
##########################
resource "aws_db_instance" "bad_rds" {
  allocated_storage    = 200 # too large for dev
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  name                 = "baddb"
  username             = "admin"
  password             = "password123"  # insecure
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true
  multi_az             = false          # No HA
  publicly_accessible  = true           # Insecure
}

##########################
# S3 Bucket (Public, unversioned)
##########################
resource "aws_s3_bucket" "bad_bucket" {
  bucket = "terrible-bucket-12345678"
  acl    = "public-read" # Insecure
}