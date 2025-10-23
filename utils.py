import json
import datetime
from gensim.models import Word2Vec

MEMORY_FILE = "memory.json"

# -------------------- ПАМЯТЬ --------------------
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"history": [], "users": {}, "word_stats": {}, "hearts": {}, "facts": {}, "preferences": {}}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_message(username, text, mood):
    memory = load_memory()
    # история сообщений — каждая запись в одну строку, без даты
    memory.setdefault("history", []).append({"user": username, "text": text, "mood": mood})
    # список сообщений пользователя — массив
    memory.setdefault("users", {}).setdefault(username, []).append(text)
    save_memory(memory)

def add_heart(username):
    memory = load_memory()
    memory.setdefault("hearts", {}).setdefault(username, 0)
    memory["hearts"][username] += 1
    save_memory(memory)

def remember_fact(username, key, value):
    memory = load_memory()
    memory.setdefault("facts", {}).setdefault(username, {})[key] = value
    save_memory(memory)

def recall_fact(username, key):
    memory = load_memory()
    return memory.get("facts", {}).get(username, {}).get(key)

def set_user_preference(username, key, value):
    memory = load_memory()
    memory.setdefault("preferences", {}).setdefault(username, {})[key] = value
    save_memory(memory)

def get_user_preference(username, key):
    memory = load_memory()
    return memory.get("preferences", {}).get(username, {}).get(key)

# -------------------- ОБУЧЕНИЕ МОДЕЛЕЙ --------------------
def train_word2vec(memory):
    sentences = [msg["text"].split() for msg in memory.get("history", []) if "text" in msg]
    if len(sentences) < 2:
        return None
    return Word2Vec(sentences, vector_size=200, window=5, min_count=1, workers=4)

def build_markov_chain(memory):
    chain = {}
    for msg in memory.get("history", []):
        words = msg.get("text", "").split()
        for i in range(len(words)-1):
            chain.setdefault(words[i], []).append(words[i+1])
    return chain

def find_similar_question(memory, question):
    words = set(question.lower().split())
    best_match = None
    max_overlap = 0
    for msg in memory.get("history", []):
        msg_words = set(msg.get("text", "").lower().split())
        overlap = len(words & msg_words)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = msg.get("text")
    return best_match if max_overlap > 0 else None