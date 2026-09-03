import asyncio
from datetime import datetime
from config import Config
from db import Database
from services.llm_service import LLMService


class PromptService:

    @classmethod
    def get_prompt_template(cls, prompt_id=None):
        """
        Step 2: Fetch the prompt template from MongoDB.
        If no prompt_id is given, use 'Education_Prompt' by default.
        """
        if not prompt_id:
            prompt_id = Config.DEFAULT_PROMPT_ID

        prompts_col = Database.get_prompts_collection()
        prompt_doc = prompts_col.find_one({"_id": prompt_id})

        if not prompt_doc:
            Database.seed_default_prompts()
            prompt_doc = prompts_col.find_one({"_id": prompt_id})

        if not prompt_doc:
            raise ValueError(f"Prompt template '{prompt_id}' was not found in the database.")

        return prompt_doc

    @classmethod
    def interpolate_template(cls, template_str, user_input):
        """
        Step 3: Replace {{userInput}} in the template with actual user input.
        """
        rendered = template_str.replace("{{userInput}}", user_input)
        rendered = rendered.replace("{{ userInput }}", user_input)
        return rendered

    @classmethod
    def process_single(cls, user_input, prompt_id=None):
        """
        Handles Single Input (Step 1 to Step 5):
        1. Get template from MongoDB
        2. Put user input into template
        3. Call LLM
        4. Save to history collection in MongoDB
        5. Return response
        """
        if not user_input or not user_input.strip():
            raise ValueError("userInput cannot be empty.")

        user_input = user_input.strip()

        prompt_doc = cls.get_prompt_template(prompt_id)
        template_text = prompt_doc["template"]
        used_prompt_id = prompt_doc["_id"]

        rendered_prompt = cls.interpolate_template(template_text, user_input)

        response_text, latency_ms, is_mock = LLMService.call_llm_single(rendered_prompt)

        history_record = {
            "prompt_id": used_prompt_id,
            "userInput": user_input,
            "renderedPrompt": rendered_prompt,
            "response": response_text,
            "timestamp": datetime.utcnow(),
            "latency_ms": latency_ms,
            "is_mock": is_mock,
            "batch_mode": False
        }
        history_col = Database.get_history_collection()
        history_col.insert_one(history_record)

        return {
            "response": response_text
        }

    @classmethod
    def process_batch(cls, user_inputs, prompt_id=None):
        """
        Handles Batch Input (Step 6):
        1. Get template
        2. Render all inputs
        3. Call LLM asynchronously in parallel
        4. Save all records to MongoDB history
        5. Return responses in same order
        """
        if not user_inputs or not isinstance(user_inputs, list):
            raise ValueError("inputs must be a non-empty list of strings.")

        cleaned_inputs = []
        for text in user_inputs:
            if not text or not str(text).strip():
                raise ValueError("List items cannot be empty.")
            cleaned_inputs.append(str(text).strip())

        # 1. Fetch template
        prompt_doc = cls.get_prompt_template(prompt_id)
        template_text = prompt_doc["template"]
        used_prompt_id = prompt_doc["_id"]

        # 2. Render all prompts
        rendered_prompts = [
            cls.interpolate_template(template_text, text)
            for text in cleaned_inputs
        ]

        # 3. Call LLM asynchronously
        batch_results = asyncio.run(
            LLMService.call_llm_batch_async(rendered_prompts)
        )

        # 4. Save each request/response to MongoDB history
        history_records = []
        response_list = []
        now = datetime.utcnow()

        for idx, (resp_text, latency_ms, is_mock) in enumerate(batch_results):
            response_list.append(resp_text)
            history_records.append({
                "prompt_id": used_prompt_id,
                "userInput": cleaned_inputs[idx],
                "renderedPrompt": rendered_prompts[idx],
                "response": resp_text,
                "timestamp": now,
                "latency_ms": latency_ms,
                "is_mock": is_mock,
                "batch_mode": True,
                "batch_index": idx
            })

        if history_records:
            history_col = Database.get_history_collection()
            history_col.insert_many(history_records)

        # 5. Return list of responses in same order (Step 6)
        return {
            "responses": response_list
        }
