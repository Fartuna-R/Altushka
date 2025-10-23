import random
import json
import datetime
import re
from utils import add_message, load_memory, build_markov_chain
from gensim.models import Word2Vec

MEMORY_FILE = "memory.json"
# -------------------- ОПРЕДЕЛЕНИЕ НАСТРОЕНИЯ --------------------
def detect_mood(text):
    """
    Определяем, хорошее или плохое сообщение.
    """
    bad_words = ["дурак", "тупой", "идиот", "ненавижу", "жопа", "пошла", "хуй", "бесит"]
    good_words = ["спасибо", "классно", "отлично", "ура", "люблю", "супер", "круто", "радость"]
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in bad_words):
        return "bad"
    elif any(word in text_lower for word in good_words):
        return "good"
    else:
        # если нет явных слов, выбираем нейтральное "good" по умолчанию
        return "good"

# -------------------- ДОБАВЛЕНИЕ СООБЩЕНИЯ С НАСТРОЕНИЕМ --------------------
def add_message_with_mood(username, text):
    mood = detect_mood(text)
    add_message(username, text, mood)
    return mood

# -------------------- ГЕНЕРАЦИЯ ОТВЕТА ВИКИ --------------------
def vika_reply(message_text, username=None):
    memory = load_memory()
    
    # очистка текста
    text = re.sub(r"@\w+", "", message_text)
    text = re.sub(r"(https?://\S+)", "", text)
    text = re.sub(r"[^\w\s\?]", "", text).strip()
    if not text:
        return "Эммм… пусто пока 😅"
    
    # определяем настроение входного сообщения
    mood = add_message_with_mood(username or "unknown", text)
    
    # выбираем подходящие прошлые сообщения по настроению
    past_msgs = [msg for msg in memory.get("history", []) if msg.get("mood") == mood]
    
    # собираем слова из истории или из текущего сообщения
    context_words = []
    if past_msgs:
        context_words = [word for msg in past_msgs[-50:] for word in msg["text"].split()]
    if not context_words:
        context_words = text.split()
    
    # Markov + случайный выбор слов
    markov = build_markov_chain(memory)
    reply_words = []
    current_word = random.choice(context_words)
    
    # определяем желаемую длину ответа (адаптивно)
    min_len = max(4, len(text.split()) // 2)
    max_len = max(6, len(text.split()) * 2)
    reply_len = random.randint(min_len, max_len)
    
    for i in range(reply_len):
        # иногда вставляем "задумку"
        if random.random() < 0.1:
            reply_words.append(random.choice(["эээ", "ну", "хм", "ладно"]))
        
        reply_words.append(current_word)
        
        next_words = markov.get(current_word)
        if next_words:
            current_word = random.choice(next_words)
        else:
            current_word = random.choice(context_words)
    
    # формируем предложения, чтобы мысль была завершена
    sentence_endings = [".", "!", "?"]
    reply = " ".join(reply_words).strip()
    if reply[-1] not in sentence_endings:
        reply += random.choice([".", "!", "?"])
    
    # редкое упоминание имени
    if username and random.random() < 0.1:
        reply = f"{username}, {reply}"
    
    return reply
