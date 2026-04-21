import json
from deep_translator import GoogleTranslator

def test():
    translator = GoogleTranslator(source='en', target='ta')
    text = "Sarathkumar\nNandhini\nLakshmi\nAmul\nRevathi"
    try:
        translated = translator.translate(text)
        print(translated)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
