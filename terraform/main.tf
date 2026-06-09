########################################
# Ubuntu AMI (Dynamic)
########################################

  data "aws_ami" "ubuntu"{
  most_recent = true

  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

########################################
# VPC
########################################

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "chatops-vpc"
  }
}

########################################
# Internet Gateway
########################################

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "chatops-igw"
  }
}

########################################
# Public Subnet
########################################

resource "aws_subnet" "public" {
   vpc_id                  = aws_vpc.main.id
   cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-west-3a"
  map_public_ip_on_launch = true

  tags = {
    Name = "chatops-public-subnet"
  }
}

########################################
# Route Table
########################################

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "chatops-public-rt"
  }
}

########################################
# Route Table Association
########################################

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

########################################
# Security Group
########################################

resource "aws_security_group" "chatops_sg" {
  name        = "chatops-security-group"
  description = "Allow SSH, HTTP, HTTPS, FastAPI, Grafana, Prometheus"
  vpc_id      = aws_vpc.main.id

  ####################################
  # SSH
  ####################################

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # HTTP
  ####################################

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # HTTPS
  ####################################

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # Frontend React / Next.js
  ####################################

  ingress {
    description = "Frontend"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # FastAPI Backend
  ####################################

  ingress {
    description = "FastAPI"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # Grafana
  ####################################

  ingress {
    description = "Grafana"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # Prometheus
  ####################################

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ####################################
  # Outbound
  ####################################

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "chatops-security-group"
  }
}

########################################
# EC2 Instance
########################################

resource "aws_instance" "chatops_ec2" {
  ami                         = "ami-0be40a46b4111e7f5"
  instance_type               = "t3.micro"
  key_name                    = var.key_name
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.chatops_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "chatops-ec2"
  }
}

