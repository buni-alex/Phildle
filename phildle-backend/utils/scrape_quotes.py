import wikiquotes
from langdetect import detect

def get_philosopher_quotes(philosopher):
    try:
        # Use search to get possible matches
        search_results = wikiquotes.search(philosopher, 'en')
        if not search_results:
            return None
        
        # Check if the first result matches exactly (case-insensitive)
        first_result = search_results[0]
        if first_result.lower() != philosopher.lower():
            # Not an exact match, so skip
            print(f"No exact match for {philosopher}, got search result: {first_result}")
            return None
        
        # Exact match found, get quotes now
        quotes = wikiquotes.get_quotes(first_result, 'en')
        if quotes:
            en_quotes = []
            for q in quotes:
                if not q.strip() or 'ISBN' in q or '.com' in q or len(q.split()) < 3:
                    continue
                try:
                    if detect(q) == 'en':
                        en_quotes.append(q)
                except Exception:
                    continue  # skip if detect fails
            return en_quotes
    except Exception as e:
        print(f"Wikiquotes error for {philosopher}: {e}")
    return None

if __name__ == "__main__":
    quotes = get_philosopher_quotes('Immanuel Kant')
    print(quotes)
    print(len(quotes))