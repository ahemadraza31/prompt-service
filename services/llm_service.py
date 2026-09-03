import asyncio
import logging
import time
from typing import List, Tuple
from config import Config

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. Falling back to Mock LLM.")


class LLMService:
    """
    Handles single and asynchronous batch calls to OpenAI (or Mock fallback).
    """
    _sync_client = None
    _async_client = None

    @classmethod
    def _get_sync_client(cls):
        if cls._sync_client is None and OPENAI_AVAILABLE and not Config.is_mock_llm():
            cls._sync_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        return cls._sync_client

    @classmethod
    def _get_async_client(cls):
        if cls._async_client is None and OPENAI_AVAILABLE and not Config.is_mock_llm():
            cls._async_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        return cls._async_client

    @classmethod
    def _generate_mock_response(cls, prompt: str) -> str:
        """
        Generates realistic domain responses when OpenAI API key is not provided.
        """
        prompt_lower = prompt.lower()
        if "ca final" in prompt_lower or "score" in prompt_lower:
            return (
                "According to ICAI guidelines for the CA Final examination:\n"
                "1. Individual Subject Requirement: You must secure a minimum of 40 marks out of 100 in each paper.\n"
                "2. Aggregate Requirement: You must achieve an overall aggregate of at least 50% across all papers in the group (or across both groups if appearing simultaneously).\n"
                "3. Exemption: Scoring 60+ marks in any paper entitles you to an exemption for that paper in the subsequent 3 attempts."
            )
        elif "foundation" in prompt_lower:
            return (
                "For the CA Foundation exam, the passing criteria is:\n"
                "1. Minimum 40% marks in each individual paper.\n"
                "2. An aggregate of at least 50% across all four papers combined."
            )
        elif "career" in prompt_lower or "jobs" in prompt_lower:
            return (
                "After qualifying as a Chartered Accountant (CA), top career avenues include:\n"
                "- Statutory & Internal Auditing\n"
                "- Corporate Finance & Investment Banking\n"
                "- Direct & Indirect Taxation Consultancy\n"
                "- Financial Advisory & Management Consulting\n"
                "- Entrepreneurship and Independent Practice"
            )
        else:
            return (
                "As an education expert, here is the answer to your query: "
                "Understanding foundational principles, thorough revision, and regular practice "
                "with past examination papers are essential to excel in this topic."
            )

    @classmethod
    def call_llm_single(cls, full_prompt: str) -> Tuple[str, float, bool]:
        """
        Synchronous single LLM call.
        Returns: (response_text, latency_ms, is_mock)
        """
        start_time = time.time()

        if Config.is_mock_llm() or not OPENAI_AVAILABLE:
            time.sleep(0.05) 
            response_text = cls._generate_mock_response(full_prompt)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return response_text, latency_ms, True

        try:
            client = cls._get_sync_client()
            completion = client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            response_text = completion.choices[0].message.content.strip()
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return response_text, latency_ms, False
        except Exception as e:
            logger.error("OpenAI API call failed: %s. Falling back to Mock.", e)
            response_text = cls._generate_mock_response(full_prompt)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return response_text, latency_ms, True

    @classmethod
    async def _call_llm_async_single(cls, full_prompt: str, index: int) -> Tuple[int, str, float, bool]:
        """
        Async worker for a single prompt that retains its original index.
        Returns: (original_index, response_text, latency_ms, is_mock)
        """
        start_time = time.time()

        if Config.is_mock_llm() or not OPENAI_AVAILABLE:
            await asyncio.sleep(0.08)
            response_text = cls._generate_mock_response(full_prompt)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return index, response_text, latency_ms, True

        try:
            client = cls._get_async_client()
            completion = await client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            response_text = completion.choices[0].message.content.strip()
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return index, response_text, latency_ms, False
        except Exception as e:
            logger.error("Async OpenAI API call failed for item %d: %s. Falling back to Mock.", index, e)
            response_text = cls._generate_mock_response(full_prompt)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return index, response_text, latency_ms, True

    @classmethod
    async def call_llm_batch_async(cls, full_prompts: List[str]) -> List[Tuple[str, float, bool]]:
        """
        Executes a batch of prompts asynchronously in parallel (Step 6).
        Preserves the exact original order of the input list.
        Returns: List of (response_text, latency_ms, is_mock)
        """
        if not full_prompts:
            return []

        tasks = [
            cls._call_llm_async_single(prompt, idx)
            for idx, prompt in enumerate(full_prompts)
        ]

        results = await asyncio.gather(*tasks)

        sorted_results = sorted(results, key=lambda item: item[0])

        return [(res[1], res[2], res[3]) for res in sorted_results]
