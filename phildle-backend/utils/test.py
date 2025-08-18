import requests
from bs4 import BeautifulSoup
import mwparserfromhell
import re
import wptools

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
        name = template.name.strip().lower()
        if name.startswith("infobox"):
            print(template)
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

def extract_clean_school_names(wikitext):
    cleaned = remove_refs_and_templates(wikitext)
    wikicode = mwparserfromhell.parse(cleaned)
    names = []
    for node in wikicode.filter():
        # Handle Wikilinks
        if isinstance(node, mwparserfromhell.nodes.Wikilink):
            text = node.text if node.text else node.title
            names.append(str(text).strip())

        # Handle plain text list items like: "| Foundationalism"
        elif isinstance(node, mwparserfromhell.nodes.Text):
            # Split lines and filter out trash
            for line in node.value.splitlines():
                stripped = line.strip()
                if stripped.startswith('|'):
                    candidate = stripped.lstrip('|').strip()
                    if candidate and not candidate.startswith('{{') and not candidate.startswith('<!--'):
                        names.append(candidate)

    return list(dict.fromkeys(names))  # preserve order, remove duplicates
# Example usage
title = "Emil_Cioran"
raw_wikitext = get_raw_wikitext(title)
school_field = extract_infobox_field(raw_wikitext, ["school_tradition", "school"])
print(extract_clean_school_names(school_field))
