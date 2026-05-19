variable "key_name" {
  description = "AWS EC2 Key Pair"
  type        = string
}
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-west-3"
}