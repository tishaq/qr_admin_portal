import boto3
import os

region = os.environ.get("AWS_REGION", "eu-west-3")
dynamodb = boto3.resource("dynamodb", region_name=region)

admins_table = dynamodb.Table("admins")
tickets_table = dynamodb.Table("tickets")
logs_table = dynamodb.Table("logs")