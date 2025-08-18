from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random

# DB setup
DATABASE_URL = "postgresql://postgres:Alex-x1410@localhost:5432/phildle"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load views and tables
playable_philosopher = Table('playable_philosopher', metadata, autoload_with=engine)
playable_quote = Table('playable_quote', metadata, autoload_with=engine)
past_phildle = Table('past_phildle', metadata, autoload_with=engine)

with Session(engine) as session:
    session.execute(past_phildle.delete())
    session.commit()  # <- don't forget this!

with Session(engine) as session:
    # Load all previously used quote IDs
    used_quote_ids = set(
        session.execute(select(past_phildle.c.quote_id)).scalars().all()
    )

    # Get the latest played_on date to schedule next set
    latest_date = session.execute(select(func.max(past_phildle.c.played_on))).scalar()
    start_day = (latest_date or date.today()) + timedelta(days=1)

    # Load philosopher IDs and weights
    philosopher_data = session.execute(
        select(playable_philosopher.c.id, playable_philosopher.c.weight)
    ).all()

    philosopher_ids = [row[0] for row in philosopher_data]
    weights = [float(row[1]) for row in philosopher_data]

    # Generate 365 new entries
    scheduled_days = []
    picked_philosophers = random.choices(philosopher_ids, weights=weights, k=365)

    for day_offset, philosopher_id in enumerate(picked_philosophers):
        played_on = start_day + timedelta(days=day_offset)

        # Get all quotes for this philosopher
        all_quotes = session.execute(
            select(playable_quote.c.id).where(
                playable_quote.c.philosopher_id == philosopher_id
            )
        ).scalars().all()

        # Filter out used quotes
        unused_quotes = [qid for qid in all_quotes if qid not in used_quote_ids]

        if unused_quotes:
            quote_id = random.choice(unused_quotes)
            used_quote_ids.add(quote_id)  # prevent reuse within same script run
        elif all_quotes:
            quote_id = random.choice(all_quotes)  # fallback: reuse
        else:
            continue  # no quotes at all

        scheduled_days.append({
            "phiolosopher_id": philosopher_id,
            "quote_id": quote_id,
            "played_on": played_on
        })

    # Bulk insert
    session.execute(past_phildle.insert(), scheduled_days)
    session.commit()