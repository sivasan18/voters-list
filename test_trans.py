import json
from googletrans import Translator
import asyncio

async def test():
    translator = Translator()
    text = "Sarathkumar\nNandhini\nLakshmi\nAmul\nRevathi"
    try:
        translated = await translator.translate(text, src='en', dest='ta')
        print(translated.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
