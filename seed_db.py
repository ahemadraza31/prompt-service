"""
seed_db.py
Script to populate the MongoDB database with initial prompt templates.
"""
from db import Database

DEFAULT_PROMPTS = [
    {
        "_id": "Education_Prompt",
        "template": "You are an expert in education domain. Answer the following: {{userInput}}",
        "description": "Explains educational concepts."
    },
    {
        "_id": "Tech_Interview_Prompt",
        "template": "You are a senior tech interviewer. Ask 3 follow-up technical questions about: {{userInput}}",
        "description": "Generates technical interview questions."
    },
    {
        "_id": "General_Prompt",
        "template": "Summarize the following topic in 2 concise sentences: {{userInput}}",
        "description": "Provides a quick two-sentence summary."
    }
]

def seed_database():
    print("Connecting to database...")
    prompts_collection = Database.get_prompts_collection()

    print("\nSeeding prompt templates...")
    for prompt in DEFAULT_PROMPTS:
        prompts_collection.update_one(
            {"_id": prompt["_id"]},
            {"$set": prompt},
            upsert=True
        )
        print(f"  [SEEDED] {prompt['_id']}")

    total_count = prompts_collection.count_documents({})
    print(f"\nDatabase seeding complete! Total prompts in DB: {total_count}")

if __name__ == "__main__":
    seed_database()
