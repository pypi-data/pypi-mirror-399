def magic_greet(name):
    import random
    greetings = ["Hello", "Hola", "Bonjour", "Salam", "Namaste"]
    emojis = ["✨", "🚀", "🐍", "💻", "🎉"]
    return f"{random.choice(greetings)} {name}! {random.choice(emojis)}"

def reverse_text(text):
    return text[::-1]
