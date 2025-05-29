import streamlit as st
import re
import os
from symspellpy.symspellpy import SymSpell, Verbosity

st.set_page_config(page_title="Fellow Formal Speech Generator", page_icon="📝", layout="centered")

# Load SymSpell
def load_symspell():
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    dictionary_path = os.path.join("frequency_dictionary_en_82_765.txt")  # Ensure this file is available
    if not sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1):
        st.error("Dictionary file not found. Please download 'frequency_dictionary_en_82_765.txt' and place it in the script directory.")
    return sym_spell

sym_spell = load_symspell()

# Dictionary for chat shortcuts to formal English expansions
CHAT_SHORTCUTS = {
    "u": "you", "ur": "your", "r": "are", "pls": "please", "plz": "please", 
    "thx": "thanks", "ty": "thank you", "idk": "I don't know", "imo": "in my opinion", 
    "btw": "by the way", "brb": "be right back", "lol": "laughing out loud", "gr8": "great", 
    "l8r": "later", "y": "why", "cya": "see you", "np": "no problem", "omg": "oh my god", 
    "b4": "before", "msg": "message", "thru": "through", "txt": "text", "k": "okay", 
    "wanna": "want to", "gonna": "going to", "gotta": "got to", "hbd": "happy birthday", 
    "hny": "happy new year", "hbd2u": "happy birthday to you", "merryxmas": "merry christmas",
    "eidmubarak": "Eid Mubarak", "happydi": "happy Diwali", "congrats": "congratulations", 
    "gratz": "congratulations", "gudluck": "good luck", "bestwishes": "best wishes", 
    "tc": "take care", "lmk": "let me know", "omw": "on my way", "ikr": "I know right", 
    "wyd": "what are you doing", "wya": "where are you",
    # Additional emojis
    "❤️": "love", "💔": "heartbroken", "😂": "laughing", "🤣": "laughing hard", 
    "😅": "nervous laugh", "😊": "smiling", "😢": "sad", "😭": "crying", "😎": "cool", 
    "😡": "angry", "😱": "shocked", "👍": "thumbs up", "👎": "thumbs down", "🙏": "please",
    "🙌": "celebration", "👏": "applause", "💯": "perfect", "🔥": "amazing", "🥺": "please",
    "🤔": "thinking", "😴": "sleepy", "✨": "sparkling", "🥳": "celebration", "🤯": "mind blown",
    "😇": "innocent", "😬": "awkward", "😤": "frustrated"
}

# Polishing dictionary: informal or simple phrase to more polished formal alternative
POLISHING_DICT = {
    "thanks": "thank you", "thank you": "I appreciate it", "great": "excellent", 
    "good": "commendable", "okay": "acceptable", "can't": "cannot", "don't": "do not", 
    "won't": "will not", "shouldn't": "should not", "i'm": "I am", "i've": "I have", 
    "let's": "let us", "you're": "you are", "it's": "it is", "that's": "that is", 
    "there's": "there is", "could be": "could possibly be", "a lot": "numerous", 
    "so": "very", "very good": "exceptional", "really good": "outstanding", "right now": "at this moment", 
    "maybe": "perhaps", "sorry": "I apologize", "help": "assist", "need to": "must", 
    "try to": "endeavor to", "ask": "request", "tell": "inform", "big": "substantial", 
    "small": "minor", "huge": "immense", "funny": "amusing", "get": "obtain", 
    "show": "demonstrate", "helpful": "beneficial", "important": "significant","luv": "love","luve": "love", "shoo": "so","choo": "so", "much": "much"
}

PUNCTUATION = {'.', ',', '!', '?', ';'}

def remove_excess_repeated_letters_in_text(text):
    """
    Remove excessive repeated letters in the entire text for better autocorrect performance.
    E.g., 'luuuvvveee' -> 'luuvee' (max 2 repeats)
    """
    def replace_repeats(match):
        char = match.group(1)
        return char*2
    # Regex to catch sequences of 3 or more same letters
    return re.sub(r'(.)\1{2,}', replace_repeats, text, flags=re.IGNORECASE)

def autocorrect_text(text):
    """
    Autocorrect text word-by-word using SymSpell.
    """
    words = text.split()
    corrected_words = []
    for word in words:
        # Lookup suggestions for lowercase word
        suggestions = sym_spell.lookup(word.lower(), Verbosity.CLOSEST, max_edit_distance=2)
        if suggestions:
            corrected_word = suggestions[0].term
            # Preserve capitalization if original word was capitalized
            if word.istitle():
                corrected_word = corrected_word.capitalize()
            elif word.isupper():
                corrected_word = corrected_word.upper()
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    return ' '.join(corrected_words)

def correct_and_expand(text):
    # First reduce excessive letter repeats to max 2 for better autocorrect
    reduced_text = remove_excess_repeated_letters_in_text(text)
    # Autocorrect words
    corrected = autocorrect_text(reduced_text)
    # Then expand chat shortcuts word-by-word
    tokens = corrected.split()
    final = []
    for token in tokens:
        token_lower = token.lower()
        replaced = CHAT_SHORTCUTS.get(token_lower, token)
        final.append(replaced)
    return ' '.join(final)

def remove_repeated_letters(word):
    """
    Remove repeated letters more than 2 times in a word.
    """
    return re.sub(r'(.)\1{2,}', r'\1\1', word)

def expand_chat_shortcuts(word):
    """
    If the word is a chat shortcut, replace it with formal expansion.
    """
    return CHAT_SHORTCUTS.get(word, word)

def polish_phrase(text):
    """
    Improve text formality by replacing phrases based on POLISHING_DICT.
    Matches whole words or phrases ignoring case.
    """
    keys = sorted(POLISHING_DICT.keys(), key=len, reverse=True)
    polished_text = text
    for phrase in keys:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        replacement = POLISHING_DICT[phrase]
        polished_text = re.sub(pattern, replacement, polished_text, flags=re.IGNORECASE)
    return polished_text

def clean_token(token):
    """
    Clean the token by removing repeated letters and expanding chat shortcuts.
    """
    token = remove_repeated_letters(token)
    token = expand_chat_shortcuts(token)
    return token

def clean_text(text):
    """
    Complete cleaning pipeline:
    - autocorrect with repeated letters reduced
    - expand chat shortcuts
    - lowercase and tokenize
    - remove repeated letters
    - polish phrases for formal language
    """
    text = correct_and_expand(text)
    text_lower = text.lower()
    tokens = re.findall(r"[\w']+|[.,!?;]", text_lower)
    cleaned_tokens = [clean_token(t) for t in tokens]
    if cleaned_tokens:
        cleaned_tokens[0] = cleaned_tokens[0].capitalize()
    result = ''
    for t in cleaned_tokens:
        if t in PUNCTUATION:
            result = result.rstrip() + t + ' '
        else:
            result += t + ' '
    result = result.strip()
    polished = polish_phrase(result)
    return polished

def make_sentence_formal(sentence):
    """
    Formalize sentence with some replacements and polish.
    """
    sentence = re.sub(r'\bi\b', 'I', sentence)
    replacements = {
        r"\bcan't\b": "cannot", r"\bdon't\b": "do not", r"\bwanna\b": "want to",
        r"\bgonna\b": "going to", r"\bgotta\b": "have to", r"\bshouldn't\b": "should not",
        r"\bcuz\b": "because", r"\bplz\b": "please", r"\bthx\b": "thank you",
    }
    for pattern, repl in replacements.items():
        sentence = re.sub(pattern, repl, sentence, flags=re.IGNORECASE)
    if re.match(r'^(hello|hi|hey)\b', sentence, re.IGNORECASE):
        sentence = "Greetings. " + sentence.capitalize()
    sentence = polish_phrase(sentence)
    return sentence

def generate_formal_speech(prompt, content):
    if not content.strip():
        return "Please provide content text to generate formal speech."
    cleaned_content = clean_text(content)
    sentence_endings = re.compile(r'([.!?])')
    parts = sentence_endings.split(cleaned_content)
    sentences = []
    for i in range(0, len(parts)-1, 2):
        sentence = parts[i].strip() + parts[i+1]
        sentences.append(sentence)
    if len(parts) % 2 != 0:
        sentences.append(parts[-1].strip())
    formal_sentences = [make_sentence_formal(s.strip()) for s in sentences if s.strip()]
    intro = f"Ladies and gentlemen, today I would like to talk about {prompt.strip()}."
    outro = "Thank you for your attention."
    speech_body = " ".join(formal_sentences)
    speech = f"{intro}\n\n{speech_body}\n\n{outro}"
    polished_speech = polish_phrase(speech)
    return polished_speech

def main():
    st.title("Clean Text Analyzer & Formal Speech Generator")
    st.markdown("""Enter text with informal style (chatting expressions, repeated letters, shortcuts) to **clean** it,
or use the **Formal Speech Generator** to create a polished formal talk based on your prompt and content.
This app also polishes and improves your text for sophisticated formal English.""")
    tab1, tab2 = st.tabs(["Clean Text", "Formal Speech Generator"])
    with tab1:
        user_input = st.text_area("Enter informal or chat-style text:", height=200)
        if st.button("Clean and Polish Text"):
            cleaned = clean_text(user_input)
            st.subheader("🧼 Cleaned and Polished Text")
            st.write(cleaned)
    with tab2:
        prompt = st.text_input("Speech Topic Prompt (e.g., importance of AI in education)")
        content = st.text_area("Content Text (informal or raw notes)", height=200)
        if st.button("Generate Formal Speech"):
            speech = generate_formal_speech(prompt, content)
            st.subheader("🗣️ Generated Formal Speech")
            st.write(speech)

if __name__ == "__main__":
    main()

