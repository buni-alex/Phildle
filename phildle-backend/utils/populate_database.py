from scrape_philosophers import get_raw_wikitext, get_philosopher_data, extract_intro_paragraphs, extract_infobox_image_with_attribution
from scrape_quotes import get_philosopher_quotes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
import os
from dotenv import load_dotenv
import time

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

Base = automap_base()
Base.prepare(autoload_with=engine)

Philosopher = Base.classes.philosopher
Quote = Base.classes.quote
print(hasattr(Philosopher, 'info'))  # should be True

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
        info = get_philosopher_data(name)
        if not info:
            continue

        quotes = get_philosopher_quotes('Zhuangzi')
        if not quotes:
            continue

        print(f"Saving {name} ({len(quotes)} quotes)")
        save_philosopher_with_quotes(session, name, info, quotes)
    session.close()

def populate_philosophers_info(max_paragraphs=3):
    session = Session()
    philosophers = session.query(Philosopher).all()
    session.close()

    for phil in philosophers:
        populate_philosopher_info_for_name(phil.name, max_paragraphs=max_paragraphs)

def populate_philosopher_info_for_name(name, max_paragraphs=3):
    session = Session()
    failures_file = "failures_info.txt"

    try:
        phil = session.query(Philosopher).filter_by(name=name).first()
        if not phil:
            print(f"No philosopher found with name '{name}'")
            return

        print(f"Processing {phil.name}...")
        try:
            wikitext = get_raw_wikitext(phil.name)
            time.sleep(1)
            if not wikitext:
                print(f"  No wikitext found for {phil.name}, skipping.")
                with open(failures_file, "a", encoding="utf-8") as f:
                    f.write(f"{phil.name}\n")
                return

            paragraphs = extract_intro_paragraphs(wikitext, max_paragraphs)
            if not paragraphs:
                print(f"  No intro paragraphs extracted for {phil.name}, skipping.")
                with open(failures_file, "a", encoding="utf-8") as f:
                    f.write(f"{phil.name}\n")
                return

            html = ''.join(paragraphs)
            print(html)

            # Update the philosopher's info column
            session.query(Philosopher).filter_by(id=phil.id).update({"info": html})
            session.commit()
            print(f"{phil.name} updated successfully!")

        except Exception as e:
            print(f"  Failed to process {phil.name}: {e}")
            with open(failures_file, "a", encoding="utf-8") as f:
                f.write(f"{phil.name}\n")

    finally:
        session.close()

def populate_philosophers_images():
    session = Session()
    philosophers = session.query(Philosopher).all()
    session.close()

    for phil in philosophers:
        populate_philosopher_image_for_name(phil.name)


def populate_philosopher_image_for_name(name):
    session = Session()
    failures_file = "failures_images.txt"

    try:
        phil = session.query(Philosopher).filter_by(name=name).first()
        if not phil:
            print(f"No philosopher found with name '{name}'")
            return

        print(f"Processing image for {phil.name}...")
        try:
            wikitext = get_raw_wikitext(phil.name)
            time.sleep(2)
            if not wikitext:
                print(f"  No wikitext found for {phil.name}, skipping.")
                with open(failures_file, "a", encoding="utf-8") as f:
                    f.write(f"{phil.name}\n")
                return

            image_info = extract_infobox_image_with_attribution(wikitext)
            if not image_info:
                print(f"  No image found for {phil.name}, skipping.")
                with open(failures_file, "a", encoding="utf-8") as f:
                    f.write(f"{phil.name}\n")
                return

            file_url = image_info["file_url"]
            attribution = image_info["attribution"]

            # Update DB
            session.query(Philosopher).filter_by(id=phil.id).update({
                "wiki_image_url": file_url,
                "wiki_image_meta": attribution  # JSONB column can take dict directly
            })
            session.commit()
            print(f"{phil.name} updated with image {file_url}")

        except Exception as e:
            print(f"  Failed to process {phil.name}: {e}")
            with open(failures_file, "a", encoding="utf-8") as f:
                f.write(f"{phil.name}\n")

    finally:
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

    populate_philosophers_info()