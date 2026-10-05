resource "aws_glue_job" "process_transactions" {
  name     = "process-transactions-iceberg"
  role_arn = aws_iam_role.glue_service_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.bronze.bucket}/scripts/process_transactions.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                    = "python"
    "--datatype"                        = "iceberg"
    "--datalake-formats"                = "iceberg"
    "--conf"                            = "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  worker_type       = "G.1X"
  number_of_workers = 2
}
