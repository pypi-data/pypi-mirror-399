import os
from typing import List
from pydantic import BaseModel
from vidai import Vidai

# --- Feature: Structured Output ---
# This example demonstrates extracting strongly-typed JSON data.
# Default Provider: OpenAI (Can be swapped with Anthropic, Gemini, etc.)

# 1. Define your structure
class Ingredient(BaseModel):
    name: str
    amount: str
    calories: int

class Recipe(BaseModel):
    title: str
    steps: List[str]
    ingredients: List[Ingredient]
    total_calories: int

# 2. Setup Client
api_key = os.getenv("OPENAI_API_KEY")
client = Vidai(api_key=api_key)

print("--- Structured Output (Recipe) ---")

# 3. Create Completion with response_format
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "How do I make a classic PB&J sandwich?"}
    ],
    response_format=Recipe
)

# 4. Access parsed object
recipe = response.choices[0].message.parsed
print(f"Title: {recipe.title}")
print(f"Calories: {recipe.total_calories}")
for ing in recipe.ingredients:
    print(f" - {ing.name} ({ing.amount})")
