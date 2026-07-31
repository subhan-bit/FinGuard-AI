"""
Seeds the database with generated transactions.

Usage:
    python -m app.simulator.seed_database
    python -m app.simulator.seed_database --count 10000 --fraud-rate 0.03
"""

import argparse

from app.db.database import SessionLocal, engine, Base
from app.models.transaction import Transaction
from app.simulator.generate_transactions import generate_transactions


def seed(num_transactions: int, fraud_rate: float):
    # Make sure tables exist (in case migrations haven't run, this is a safety net)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print(f"Generating {num_transactions} transactions (fraud rate: {fraud_rate*100:.1f}%)...")
        txns = generate_transactions(num_transactions=num_transactions, fraud_rate=fraud_rate)

        print("Inserting into database...")
        objects = [Transaction(**txn) for txn in txns]

        batch_size = 500
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            db.bulk_save_objects(batch)
            db.commit()
            print(f"  Inserted {min(i + batch_size, len(objects))}/{len(objects)}")

        fraud_count = sum(1 for t in txns if t["is_fraud"])
        print(f"\nDone. Inserted {len(objects)} transactions ({fraud_count} fraudulent).")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the database with fake transactions.")
    parser.add_argument("--count", type=int, default=5000, help="Number of transactions to generate")
    parser.add_argument("--fraud-rate", type=float, default=0.03, help="Fraction that should be fraudulent")
    args = parser.parse_args()

    seed(num_transactions=args.count, fraud_rate=args.fraud_rate)