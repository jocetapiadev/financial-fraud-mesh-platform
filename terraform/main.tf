provider "aws" {
  region = "us-east-1"
}

# Buckets para el Data Lake (Capa Bronze y Silver)
resource "aws_s3_bucket" "bronze" {
  bucket = "financial-datalake-bronze-dev"
}

resource "aws_s3_bucket" "silver" {
  bucket = "financial-datalake-silver-dev"
}

# Base de datos en el Glue Data Catalog
resource "aws_glue_catalog_database" "financial_db" {
  name = "financial_fraud_db"
}
