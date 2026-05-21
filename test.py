import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": "Какви са основните хранителни принципи при химиотерапия?"
    }]
)

print(response.content[0].text)