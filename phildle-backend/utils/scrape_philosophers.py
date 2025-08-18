import requests
from bs4 import BeautifulSoup
import mwparserfromhell
import re
import dateparser
from dateutil.parser import parse as dateutil_parse

def get_philosophers_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    philosophers = set()

    for ul in soup.select('div.mw-parser-output > ul')[:-1]:
        for li in ul.find_all('li', recursive=False):  # loop through list items
            a_tag = li.find('a')
            if (a_tag and a_tag.get('href', '').startswith('/wiki/')):
                name = a_tag.get_text(strip=True)
                philosophers.add(name)

    return sorted(philosophers)

def get_raw_wikitext(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': title,
        'rvslots': 'main',
        'rvprop': 'content',
    }
    response = requests.get(url, params=params)
    data = response.json()
    pages = data['query']['pages']
    for page in pages.values():
        return page['revisions'][0]['slots']['main']['*']
    return ''

def extract_infobox_field(wikitext, field_names):
    wikicode = mwparserfromhell.parse(wikitext)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name.lower().strip().startswith("infobox"):
            for field in field_names:
                if template.has(field):
                    return str(template.get(field).value.strip())
    return None

def remove_refs_and_templates(wikitext):
    # Remove everything between <ref>...</ref> (including nested)
    wikitext = re.sub(r'<ref[^>]*>.*?</ref>', '', wikitext, flags=re.DOTALL | re.IGNORECASE)
    # Remove self-closing <ref ... />
    wikitext = re.sub(r'<ref[^>]*/>', '', wikitext, flags=re.IGNORECASE)
    # Remove {{nwr|...}}, {{rp|...}}, {{Cite...}}, etc.
    wikitext = re.sub(r'\{\{(?:nwr|rp|cite[^}|]*|sfn|harv|page)[^}]*\}\}', '', wikitext, flags=re.IGNORECASE)
    # Remove leftover {{...}} blocks with known citation junk
    wikitext = re.sub(r'\{\{[^{]*?(doi|isbn|ref|page|rp|nwr)[^}]*\}\}', '', wikitext, flags=re.IGNORECASE)
    return wikitext

def extract_country(raw_country):
    cleaned = remove_refs_and_templates(raw_country)  # CLEAN FIRST
    wikicode = mwparserfromhell.parse(cleaned)

    parts = []
    for node in wikicode.nodes:
        if node.__class__.__name__ == 'Text':
            parts.append(str(node).strip())
        elif node.__class__.__name__ == 'Wikilink':
            parts.append(str(node.title).strip())
        # You can handle other node types if needed
    full_text = ', '.join(parts)
    return re.sub(r',\s*,+', ',', full_text).strip(' ,')

def normalize_date(text):
    if not text:
        return None
    try:
        # Try modern parser
        date = dateparser.parse(text, settings={'STRICT_PARSING': True})
        if date:
            return date.strftime('%Y-%m-%d')
    except Exception:
        pass

    try:
        # Try fallback with dateutil
        date = dateutil_parse(text, fuzzy=True)
        return date.strftime('%Y-%m-%d')
    except Exception:
        pass

    # Try manual match: e.g., 13 November 354
    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{1,4})\s*(BC)?', text)
    if match:
        day, month_str, year, bc = match.groups()
        try:
            month = dateutil_parse(month_str).month
            year = f"-{year}" if bc else year
            return f"{int(year)}-{int(month):02d}-{int(day):02d}"
        except Exception:
            pass

    return None

def extract_birth_date(text):
    if not text:
        return None

    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()

    for t in templates:
        if t.name.matches('birth date') or t.name.matches('birth date and age'):
            numbers = []
            for param in t.params:
                val = param.value.strip_code().strip()
                if val.isdigit():
                    numbers.append(val)
                if len(numbers) == 3:
                    break
            if len(numbers) == 3:
                year, month, day = numbers
                return f"{int(year)}-{month.zfill(2)}-{day.zfill(2)}"

        elif t.name.matches('circa'):
            year = t.get(1).value.strip_code()
            suffix = 'BC' if 'BC' in text else ''
            # Remove the 'c.' prefix by just returning the year + suffix
            return f"{year} {suffix}".strip()
    plain = wikicode.strip_code().strip()
    # Fallback to plain text cleaned version
    if plain:
        plain = re.sub(r'^[cC]\.\s*', '', plain)  # remove leading c.
        plain = re.sub(r'\s*\(.*?\)', '', plain)  # remove parentheses
        normalized = normalize_date(plain)
        return normalized or plain.strip()

    return None

#For whatever shit reason wikimedia templates for death date
#also include the birth date??
def extract_death_date(text):
    if not text:
        return None

    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()

    for t in templates:
        if t.name.matches('death date') or t.name.matches('death date and age'):
            numbers = []
            for param in t.params:
                val = param.value.strip_code().strip()
                if val.isdigit():
                    numbers.append(val)
                if len(numbers) == 3:
                    break
            if len(numbers) == 3:
                year, month, day = numbers
                year = int(year)
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        elif t.name.matches('circa'):
            year = t.get(1).value.strip_code()
            suffix = 'BC' if 'BC' in text else ''
            return f"{year} {suffix}".strip()
    plain = wikicode.strip_code().strip()
    if plain:
        plain = re.sub(r'^[cC]\.\s*', '', plain)  # remove leading c.
        plain = re.sub(r'\s*\(.*?\)', '', plain)  # remove parentheses
        normalized = normalize_date(plain)
        return normalized or plain.strip()

    return None

FILTERED_SIGNS = [":", '"', '.', "'"]
def contains_bad_substrings(s):
    bad_substrings = ['(,', ', )', '...', ']]', '])']
    for bad in bad_substrings:
        if bad in s:
            return True
    return False

def extract_school_from_wikitext(wikitext):
    if not wikitext:
        return ''

    cleaned = remove_refs_and_templates(wikitext)
    wikicode = mwparserfromhell.parse(cleaned)

    names = []
    for node in wikicode.filter():
        if isinstance(node, mwparserfromhell.nodes.Wikilink):
            text = node.text or node.title
            names.append(str(text).strip())
        elif isinstance(node, mwparserfromhell.nodes.Text):
            for line in node.value.splitlines():
                stripped = line.strip()
                if stripped.startswith('|'):
                    candidate = stripped.lstrip('|').strip()
                    if candidate and not candidate.startswith('{{') and not candidate.startswith('<!--'):
                        names.append(candidate)

    # Filtering logic from original extract_school()
    seen = set()
    final = []
    for part in ', '.join(names).split(','):
        p = part.strip()
        if (p and 
            p.lower() not in seen and
            #len(p.split()) < 6 and
            #not any(char in p for char in FILTERED_SIGNS) and
            #p not in {'(', ')'} and
            not any(char.isdigit() for char in p) and
            not contains_bad_substrings(p)
            ):
            seen.add(p.lower())
            final.append(p)

    return ', '.join(final)

def get_field_combined(wikitext, *fields):
    values = []
    for field in fields:
        val = extract_infobox_field(wikitext, [field])
        if val:
            values.append(val)
    if values:
        return " ".join(values)
    return None

def get_philosopher_info(name):
    try:
        wikitext = get_raw_wikitext(name)
        if not wikitext:
            return None

        def get_field(*fields):
            return extract_infobox_field(wikitext, fields)

        info = {}

        raw_birth = get_field('birth_date')
        raw_death = get_field('death_date')
        raw_nationality = get_field('birth_place', 'nationality')
        raw_school = get_field_combined(wikitext, 'era', 'school_tradition', 'school', 'tradition')

        info['birth'] = extract_birth_date(raw_birth or '')
        info['death'] = extract_death_date(raw_death or '')
        info['country'] = extract_country(remove_refs_and_templates(raw_nationality or ''))
        info['school'] = extract_school_from_wikitext(remove_refs_and_templates(raw_school or ''))

        return info
    except Exception as e:
        print(f"error for {name}: {e}")
        return None
    
if __name__ == '__main__':
    # Example usage:
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

    #print(f"Total unique philosophers across centuries: {len(all_philosophers)}")

    info = get_philosopher_info('Edmund_Husserl')
    print(info)