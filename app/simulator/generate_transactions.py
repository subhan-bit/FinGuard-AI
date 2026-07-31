"""
Transaction Simulator for FinGuard AI

Generates realistic card transactions, with a small percentage
engineered to look fraudulent based on known fraud patterns:
- Unusually high amounts
- Odd hours (late night)
- Foreign/high-risk countries
- High-risk merchant categories
- Rapid repeated transactions (velocity)
"""

import random
import uuid
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()

MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "electronics", "clothing",
    "travel", "gas_station", "pharmacy", "entertainment",
    "online_retail", "utilities", "gambling", "crypto_exchange",
    "jewelry", "electronics_high_value"
]

HIGH_RISK_CATEGORIES = ["gambling", "crypto_exchange", "jewelry", "electronics_high_value"]

COUNTRIES = ["US", "GB", "DE", "FR", "CA", "AU", "JP"]
HIGH_RISK_COUNTRIES = ["NG", "RU", "KP", "IR", "PK"]

CURRENCIES = {
    "US": "USD", "GB": "GBP", "DE": "EUR", "FR": "EUR",
    "CA": "CAD", "AU": "AUD", "JP": "JPY",
    "NG": "NGN", "RU": "RUB", "KP": "KPW", "IR": "IRR", "PK": "PKR"
}


def generate_legit_transaction(card_id: str, base_time: datetime) -> dict:
    """Generate a normal, non-fraudulent transaction."""
    country = random.choice(COUNTRIES)
    category = random.choice(MERCHANT_CATEGORIES)

    # Normal transactions happen during reasonable hours, reasonable amounts
    hour_offset = random.randint(7, 22)  # 7am - 10pm
    timestamp = base_time.replace(
        hour=hour_offset, minute=random.randint(0, 59)
    )

    amount = round(random.uniform(5, 300), 2)
    if category in ["travel", "electronics"]:
        amount = round(random.uniform(50, 800), 2)

    return {
        "id": str(uuid.uuid4()),
        "card_id": card_id,
        "merchant": fake.company(),
        "merchant_category": category,
        "amount": amount,
        "currency": CURRENCIES[country],
        "country": country,
        "timestamp": timestamp,
        "is_fraud": False,
    }


def generate_fraud_transaction(card_id: str, base_time: datetime) -> dict:
    """Generate a transaction engineered to look fraudulent."""
    fraud_pattern = random.choice(["high_amount", "odd_hour", "risky_country", "risky_category"])

    country = random.choice(COUNTRIES)
    category = random.choice(MERCHANT_CATEGORIES)
    amount = round(random.uniform(5, 300), 2)
    hour_offset = random.randint(7, 22)

    if fraud_pattern == "high_amount":
        amount = round(random.uniform(1000, 9000), 2)

    elif fraud_pattern == "odd_hour":
        hour_offset = random.choice([0, 1, 2, 3, 4])

    elif fraud_pattern == "risky_country":
        country = random.choice(HIGH_RISK_COUNTRIES)
        amount = round(random.uniform(200, 3000), 2)

    elif fraud_pattern == "risky_category":
        category = random.choice(HIGH_RISK_CATEGORIES)
        amount = round(random.uniform(500, 5000), 2)

    timestamp = base_time.replace(
        hour=hour_offset, minute=random.randint(0, 59)
    )

    return {
        "id": str(uuid.uuid4()),
        "card_id": card_id,
        "merchant": fake.company(),
        "merchant_category": category,
        "amount": amount,
        "currency": CURRENCIES.get(country, "USD"),
        "country": country,
        "timestamp": timestamp,
        "is_fraud": True,
    }


def generate_transactions(num_transactions: int = 5000, fraud_rate: float = 0.03) -> list[dict]:
    """
    Generate a batch of transactions.

    Args:
        num_transactions: total number of transactions to generate
        fraud_rate: fraction that should be fraudulent (e.g. 0.03 = 3%)
    """
    transactions = []
    num_cards = max(50, num_transactions // 20)  # simulate a pool of cards
    card_ids = [f"card_{i:05d}" for i in range(num_cards)]

    num_fraud = int(num_transactions * fraud_rate)
    num_legit = num_transactions - num_fraud

    start_date = datetime.now() - timedelta(days=90)

    for _ in range(num_legit):
        card_id = random.choice(card_ids)
        day_offset = random.randint(0, 90)
        base_time = start_date + timedelta(days=day_offset)
        transactions.append(generate_legit_transaction(card_id, base_time))

    for _ in range(num_fraud):
        card_id = random.choice(card_ids)
        day_offset = random.randint(0, 90)
        base_time = start_date + timedelta(days=day_offset)
        transactions.append(generate_fraud_transaction(card_id, base_time))

    random.shuffle(transactions)
    return transactions


if __name__ == "__main__":
    txns = generate_transactions(num_transactions=100, fraud_rate=0.03)
    print(f"Generated {len(txns)} transactions")
    print(f"Fraudulent: {sum(1 for t in txns if t['is_fraud'])}")
    print("\nSample transaction:")
    print(txns[0])