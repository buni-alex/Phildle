import requests
from bs4 import BeautifulSoup
import mwparserfromhell
import re
import dateparser
from dateutil.parser import parse as dateutil_parse
import urllib

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
    if response.status_code != 200:
        print(f"Failed to fetch {title}: HTTP {response.status_code}")
        return None

    try:
        data = response.json()
    except ValueError:
        print(f"Failed to decode JSON for {title}: {response.text[:200]}")
        return None
    
    pages = data['query']['pages']
    for page in pages.values():
        return page['revisions'][0]['slots']['main']['*']
    return ''

def extract_intro_paragraphs(wikitext, max_paragraphs=3):
    # Collapse single newlines but preserve paragraph breaks
    wikitext = re.sub(r'(?<!\n)\n(?!\n)', ' ', wikitext)
    # Remove HTML comments
    wikitext = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)

    wikicode = mwparserfromhell.parse(wikitext)

    # Remove refs and citation templates
    for tag in wikicode.filter_tags(matches=lambda t: t.tag.lower() == 'ref'):
        wikicode.remove(tag)
    for template in wikicode.filter_templates():
        if template.name.lower().startswith("cite"):
            wikicode.remove(template)

    paragraphs = []
    buffer = []

    def finalize_paragraph(buf):
        paragraph = ''.join(buf).replace('\n\n', ' ').strip()
        paragraph = clean_paragraph(paragraph)
        if not paragraph:
            return None

        # Remove wiki-style brackets [[word]] → word
        paragraph = re.sub(r'\[\[([^\[\]]+)\]\]', r'\1', paragraph)

        # Fix parentheses in first sentence
        sentence_end = max(paragraph.find('.'), paragraph.find('!'), paragraph.find('?'))
        first_sentence = paragraph if sentence_end == -1 else paragraph[:sentence_end+1]

        def clean_parens(match):
            content = match.group(1)
            cleaned = re.sub(r'^[^A-Za-z0-9]+', '', content)
            return f'({cleaned})'

        first_sentence = re.sub(r'\((.*?)\)', clean_parens, first_sentence)

        if sentence_end != -1:
            rest = paragraph[sentence_end+1:]
            paragraph = first_sentence + rest
        else:
            paragraph = first_sentence

        # Truncate paragraph at last proper punctuation
        last_punct = max(paragraph.rfind('.'), paragraph.rfind('!'), paragraph.rfind('?'))
        if last_punct != -1:
            paragraph = paragraph[:last_punct+1]

        return f"<p>{paragraph}</p>"

    for node in wikicode.nodes:
        if isinstance(node, mwparserfromhell.nodes.Heading):
            break
        if isinstance(node, mwparserfromhell.nodes.Template):
            continue
        if isinstance(node, mwparserfromhell.nodes.Wikilink) and str(node.title).lower().startswith('file:'):
            continue

        text = str(node)

        if '\n\n' in text:
            parts = text.split('\n\n')
            for i, part in enumerate(parts):
                if part.strip():
                    buffer.append(part)
                # When we hit a paragraph break
                if i < len(parts) - 1:
                    para_html = finalize_paragraph(buffer)
                    if para_html:
                        paragraphs.append(para_html)
                    buffer = []
                    if len(paragraphs) >= max_paragraphs:
                        break
        else:
            buffer.append(text)

        if len(paragraphs) >= max_paragraphs:
            break

    # Flush remaining buffer if needed
    if buffer and len(paragraphs) < max_paragraphs:
        para_html = finalize_paragraph(buffer)
        if para_html:
            paragraphs.append(para_html)

    return paragraphs[:max_paragraphs]



def clean_paragraph(paragraph):
    # Remove leading semicolons and whitespace in parentheses
    paragraph = re.sub(r'\(\s*([;,]+\s*)+', '(', paragraph)

    # Bold / Italic
    paragraph = re.sub(r"'''(.*?)'''", r"<strong>\1</strong>", paragraph)
    paragraph = re.sub(r"''(.*?)''", r"<em>\1</em>", paragraph)

    # Parse with mwparserfromhell and flatten links
    code = mwparserfromhell.parse(paragraph)
    out = []

    for node in code.nodes:
        if isinstance(node, mwparserfromhell.nodes.Wikilink):
            link = str(node.title).strip()
            # Skip thumbnails/files
            if link.lower().startswith(("file:", "image:")):
                continue
            text = str(node.text).strip() if node.text else link
            out.append(f'<a href="https://en.wikipedia.org/wiki/{link}">{text}</a>')
        else:
            # Keep everything else (including bold/italic)
            out.append(str(node))

    paragraph = "".join(out).strip()
    paragraph = re.sub(r'\(\s*([;,]+\s*)+', '(', paragraph)
    paragraph = paragraph.replace(r"\'", "'")
    return paragraph if len(re.findall(r'[A-Za-z]', paragraph)) >= 5 else None

def extract_infobox_field(wikitext, field_names):
    wikicode = mwparserfromhell.parse(wikitext)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name.lower().strip().startswith("infobox"):
            for field in field_names:
                if template.has(field):
                    return str(template.get(field).value.strip())
    return None

def clean_extmetadata_field(value):
    """Extract plain text and first link (if any) from Wikimedia extmetadata fields."""
    if not value:
        return None, None
    soup = BeautifulSoup(value, "html.parser")
    # Extract first link if present
    link = soup.find("a")
    url = link["href"] if link and link.has_attr("href") else None
    # Clean plain text
    text = soup.get_text(" ", strip=True)
    return text, url

def extract_infobox_image_with_attribution(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    templates = wikicode.filter_templates()

    for template in templates:
        if template.name.lower().strip().startswith("infobox"):
            for field in ["image", "img", "image_file", "image_name", "portrait"]:
                if template.has(field):
                    raw_value = str(template.get(field).value.strip())
                    if not raw_value:
                        continue

                    # Remove markup like [[File:...|...]]
                    if "[[" in raw_value and "]]" in raw_value:
                        raw_value = raw_value.strip("[]")
                        raw_value = raw_value.split(":", 1)[-1]

                    if raw_value.lower().startswith("file:"):
                        raw_value = raw_value[5:]

                    # Only keep before first pipe if present
                    if "|" in raw_value:
                        raw_value = raw_value.split("|", 1)[0]

                    filename = raw_value.strip()
                    safe_filename = urllib.parse.quote(filename)

                    file_url = f"https://en.wikipedia.org/wiki/Special:FilePath/{safe_filename}"

                    # Attribution via Wikimedia API
                    api_url = (
                        "https://commons.wikimedia.org/w/api.php"
                        "?action=query&titles=File:" + urllib.parse.quote(filename) +
                        "&prop=imageinfo&iiprop=url|extmetadata&format=json"
                    )
                    r = requests.get(api_url)
                    data = r.json()

                    attribution = {}
                    pages = data.get("query", {}).get("pages", {})
                    for page in pages.values():
                        if "imageinfo" in page:
                            info = page["imageinfo"][0]
                            ext = info.get("extmetadata", {})

                            # Clean author
                            author_text, author_url = clean_extmetadata_field(ext.get("Artist", {}).get("value"))
                            # Clean credit
                            credit_text, credit_url = clean_extmetadata_field(ext.get("Credit", {}).get("value"))

                            attribution = {
                                "description_url": info.get("descriptionurl"),
                                "author": author_text,
                                "author_url": author_url,
                                "credit": credit_text,
                                "credit_url": credit_url,
                                "license": ext.get("LicenseShortName", {}).get("value"),
                                "license_url": ext.get("LicenseUrl", {}).get("value"),
                            }

                    # Fallback if missing on Commons
                    if not attribution:
                        print(safe_filename)
                        wiki_file_page = f"https://en.wikipedia.org/wiki/File:{safe_filename}"
                        r2 = requests.get(wiki_file_page)
                        if r2.status_code == 200:
                            soup = BeautifulSoup(r2.text, "html.parser")
                            og_image = soup.find("meta", property="og:image")
                            file_url = og_image["content"] if og_image else wiki_file_page
                            
                            # Extract license URL from link rel="license"
                            license_link = soup.find("link", rel="license")
                            license_url = license_link["href"] if license_link else None
                            
                            # Build attribution dict
                            attribution = {
                                "description_url": wiki_file_page,
                                "author": None,  # still try the table or leave None
                                "author_url": None,
                                "credit": None,
                                "credit_url": None,
                                "license": license_url,
                                "license_url": license_url,
                            }
                            
                            # Optional: try to find the author from the table as before
                            info_table = soup.find("table", class_="fileinfotpl-type-information")
                            if info_table:
                                author_tag = info_table.find("a", title=lambda x: x and "User:" in x)
                                if author_tag:
                                    attribution["author"] = author_tag.text.strip()
                                    attribution["author_url"] = "https://en.wikipedia.org" + author_tag["href"]
                    return {
                        "file_url": file_url,
                        "filename": filename,
                        "attribution": attribution
                    }
                            
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
    full_text = ', '.join(parts)
    return re.sub(r',\s*,+', ',', full_text).strip(' ,')

def normalize_date(text):
    if not text:
        return None
    try:
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
            return f"{year} {suffix}".strip()
    plain = wikicode.strip_code().strip()

    if plain:
        plain = re.sub(r'^[cC]\.\s*', '', plain)  
        plain = re.sub(r'\s*\(.*?\)', '', plain)
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

def get_philosopher_data(name):
    try:
        wikitext = get_raw_wikitext(name)
        if not wikitext:
            return None

        def get_field(*fields):
            return extract_infobox_field(wikitext, fields)

        data = {}

        raw_birth = get_field('birth_date')
        raw_death = get_field('death_date')
        raw_nationality = get_field('birth_place', 'nationality')
        raw_school = get_field_combined(wikitext, 'era', 'school_tradition', 'school', 'tradition')
        info = extract_intro_paragraphs(wikitext)

        data['birth'] = extract_birth_date(raw_birth or '')
        data['death'] = extract_death_date(raw_death or '')
        data['country'] = extract_country(remove_refs_and_templates(raw_nationality or ''))
        data['school'] = extract_school_from_wikitext(remove_refs_and_templates(raw_school or ''))
        data['info'] = info

        return data
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

    text = get_raw_wikitext('David Ricardo')
    img_url = extract_intro_paragraphs(text)
    print(img_url)