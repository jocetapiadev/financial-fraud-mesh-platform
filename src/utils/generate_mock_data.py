import os
import random
import uuid
from datetime import datetime
import pandas as pd


def generate_mock_transactions(num_records=1000):
    data = []
    customer_ids = [f"CUST_{i:04d}" for i in range(1, 51)]

    for _ in range(num_records):
        record = {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": random.choice(customer_ids),
            "amount": round(random.uniform(5.0, 15000.0), 2),
            "timestamp": datetime.now().isoformat(),
            "status": random.choice(["COMPLETED", "PENDING", "FAILED"]),
        }
        data.append(record)

    df = pd.DataFrame(data)

    # Crear directorio local si no existe
    os.makedirs("sample_data/bronze", exist_ok=True)

    # Guardar como Parquet
    output_path = "sample_data/bronze/transactions_sample.parquet"
    df.to_parquet(output_path, index=False)
    print(
        f"✅ Exitosamente generados {num_records} registros de prueba en: {output_path}"
    )


if __name__ == "__main__":
    generate_mock_transactions()
