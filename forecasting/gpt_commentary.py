import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
USE_REAL_GPT = os.getenv("USE_REAL_GPT", "false").lower() == 'true'

def _mock_comment(item):
    return (f"Mock commentary: Product {item['product_id']} has {item.get('current_stock')} units left. " 
            f"Estimated depletion in {item['days_until_depletion']:.1f} days. Suggested to reorder {item['suggested_qty']} units.")

def generate_commentary(item):
    if not USE_REAL_GPT:
        return _mock_comment(item)

    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    prompt = (f"You are an inventory analyst. Given the item: {item}, write a concise 2-3 sentence recommendation explaining why to reorder and any risks.")
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=150
    )
    return resp['choices'][0]['message']['content']

if __name__ == "__main__":
    # quick local demo: read draft_pos and print commentary
    df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'draft_pos.csv')))
    for _, r in df.iterrows():
        item = r.to_dict()
        print(generate_commentary(item))
