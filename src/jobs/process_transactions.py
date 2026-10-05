import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, when

# 1. Inicializar la sesión de Spark con soporte nativo para Iceberg + AWS Glue Catalog
spark = (
    SparkSession.builder.config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .config(
        "spark.sql.catalog.glue_catalog",
        "org.apache.iceberg.spark.SparkCatalog",
    )
    .config(
        "spark.sql.catalog.glue_catalog.warehouse",
        "s3://financial-datalake-silver-dev/",
    )
    .config(
        "spark.sql.catalog.glue_catalog.catalog-impl",
        "org.apache.iceberg.aws.glue.GlueCatalog",
    )
    .getOrCreate()
)

# 2. Leer carga incremental (Bronze Layer)
bronze_path = "s3://financial-datalake-bronze-dev/transactions/raw/"
df_raw = spark.read.format("parquet").load(bronze_path)

# 3. Transformación y Clasificación del Riesgo (Reglas AML)
df_transformed = (
    df_raw.filter(col("amount") > 0)
    .withColumn(
        "risk_level",
        when(col("amount") > 10000, "HIGH")
        .when(col("amount") > 5000, "MEDIUM")
        .otherwise("LOW"),
    )
    .withColumn("processed_at", current_timestamp())
)

# 4. Registrar Staging View
df_transformed.createOrReplaceTempView("staged_transactions")

# 5. Asegurar existencia de la Tabla Iceberg en Glue Catalog
spark.sql(
    """
    CREATE TABLE IF NOT EXISTS glue_catalog.financial_fraud_db.silver_transactions (
        transaction_id STRING,
        customer_id STRING,
        amount DOUBLE,
        risk_level STRING,
        processed_at TIMESTAMP
    )
    USING iceberg
"""
)

# 6. Operación MERGE INTO (Upsert idempotente)
spark.sql(
    """
    MERGE INTO glue_catalog.financial_fraud_db.silver_transactions t
    USING staged_transactions s
    ON t.transaction_id = s.transaction_id
    WHEN MATCHED THEN
        UPDATE SET 
            t.amount = s.amount,
            t.risk_level = s.risk_level,
            t.processed_at = s.processed_at
    WHEN NOT MATCHED THEN
        INSERT (transaction_id, customer_id, amount, risk_level, processed_at)
        VALUES (s.transaction_id, s.customer_id, s.amount, s.risk_level, s.processed_at)
"""
)

print("Procesamiento incremental completado exitosamente en Apache Iceberg.")
