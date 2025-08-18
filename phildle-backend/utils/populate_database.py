from scrape_philosophers import get_philosopher_info, get_philosophers_from_url
from scrape_quotes import get_philosopher_quotes
import re
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.ext.automap import automap_base

DATABASE_URL = "postgresql://postgres:Alex-x1410@localhost:5432/phildle"
engine = create_engine(DATABASE_URL)

Base = automap_base()
Base.prepare(engine, reflect=True)

Philosopher = Base.classes.philosopher
Quote = Base.classes.quote

Session = sessionmaker(bind=engine)

def save_philosopher_with_quotes(session, name, info, quotes):
    birth_date = info.get('birth')
    death_date = info.get('death')
    school = info.get('school')
    country = info.get('country')

    # Try to fetch existing philosopher
    philosopher = session.query(Philosopher).filter_by(name=name).first()

    if not philosopher:
        philosopher = Philosopher(
            name=name,
            school=school,
            country=country,
            birth_date=birth_date,
            death_date=death_date,
        )
        session.add(philosopher)
        session.flush()  # Get `id` before adding quotes

    for q in quotes:
        if not session.query(Quote).filter_by(text=q).first():  # avoid duplicates
            quote = Quote(text=q, philosopher_id=philosopher.id)
            session.add(quote)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Failed to save {name}: {e}")

def run_pipeline(philosophers):
    session = Session()
    for name in philosophers:
        info = get_philosopher_info(name)
        if not info:
            continue

        quotes = get_philosopher_quotes('Zhuangzi')
        if not quotes:
            continue

        print(f"Saving {name} ({len(quotes)} quotes)")
        save_philosopher_with_quotes(session, name, info, quotes)
    session.close()

if __name__ == "__main__":
    #century_urls = [
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_centuries_BC",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_1st_through_10th_centuries",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_11th_through_14th_centuries",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_15th_and_16th_centuries",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_17th_century",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_18th_century",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_19th_century",
    #    "https://en.wikipedia.org/wiki/List_of_philosophers_born_in_the_20th_century"
    #]
#
    #all_philosophers = set()
    #for url in century_urls:
    #    all_philosophers.update(get_philosophers_from_url(url))
    #run_pipeline(all_philosophers)

    run_pipeline({'Zhuang Zhou'})