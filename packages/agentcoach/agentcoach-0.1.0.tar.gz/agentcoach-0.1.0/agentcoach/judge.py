"""LLM judge adapters for quality scoring."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Union, Optional

import httpx


class Judge(ABC):
    """Base class for LLM judges."""
    
    @abstractmethod
    async def score_output(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> dict[str, Any]:
        """Score an output for quality.
        
        Returns dict with scores for:
        - accuracy_grounding
        - relevance
        - constraint_adherence
        - tone_policy
        """
        pass
    
    @abstractmethod
    def rewrite_with_evidence(
        self,
        original_answer: str,
        evidence: list[str],
        user_query: str,
    ) -> str:
        """Rewrite answer using only provided evidence."""
        pass


class OpenAIJudge(Judge):
    """OpenAI-based judge."""
    
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    async def score_output(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> dict[str, Any]:
        """Score output using OpenAI."""
        prompt = self._build_scoring_prompt(final_answer, evidence, user_query, constraints)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    return json.loads(content[start:end].strip())
                raise
    
    def rewrite_with_evidence(
        self,
        original_answer: str,
        evidence: list[str],
        user_query: str,
    ) -> str:
        """Rewrite answer using only evidence (synchronous)."""
        prompt = f"""Rewrite the following answer to use ONLY the provided evidence.
Do not add information not present in the evidence.

User Query: {user_query}

Evidence:
{chr(10).join(f"[{i+1}] {ev[:500]}" for i, ev in enumerate(evidence))}

Original Answer:
{original_answer}

Rewritten Answer (using only evidence above):"""
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _build_scoring_prompt(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> str:
        """Build prompt for scoring."""
        return f"""You are an expert evaluator of AI agent outputs. Score the following output on multiple dimensions.

User Query: {user_query}

Constraints:
{chr(10).join(f"- {c}" for c in constraints) if constraints else "None specified"}

Evidence Available:
{chr(10).join(f"[{i+1}] {ev[:300]}..." for i, ev in enumerate(evidence))}

Agent Output:
{final_answer}

Evaluate and return JSON with scores (0.0-1.0):
{{
  "accuracy_grounding": <score>,
  "relevance": <score>,
  "constraint_adherence": <score>,
  "tone_policy": <score>,
  "explanation": "<brief explanation>"
}}"""


class AnthropicJudge(Judge):
    """Anthropic Claude-based judge."""
    
    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    async def score_output(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> dict[str, Any]:
        """Score output using Anthropic."""
        prompt = self._build_scoring_prompt(final_answer, evidence, user_query, constraints)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            content = result["content"][0]["text"]
            
            # Parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    return json.loads(content[start:end].strip())
                raise
    
    def rewrite_with_evidence(
        self,
        original_answer: str,
        evidence: list[str],
        user_query: str,
    ) -> str:
        """Rewrite answer using only evidence."""
        prompt = f"""Rewrite the following answer to use ONLY the provided evidence.

User Query: {user_query}

Evidence:
{chr(10).join(f"[{i+1}] {ev[:500]}" for i, ev in enumerate(evidence))}

Original Answer:
{original_answer}

Rewritten Answer:"""
        
        with httpx.Client() as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
    
    def _build_scoring_prompt(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> str:
        """Build prompt for scoring."""
        return f"""Evaluate this AI agent output on multiple quality dimensions.

User Query: {user_query}

Constraints:
{chr(10).join(f"- {c}" for c in constraints) if constraints else "None"}

Evidence:
{chr(10).join(f"[{i+1}] {ev[:300]}..." for i, ev in enumerate(evidence))}

Output:
{final_answer}

Return JSON with scores (0.0-1.0):
{{
  "accuracy_grounding": <score>,
  "relevance": <score>,
  "constraint_adherence": <score>,
  "tone_policy": <score>,
  "explanation": "<explanation>"
}}"""


class SAPAICoreJudge(Judge):
    """SAP BTP AI Core judge (functional stub)."""
    
    def __init__(self) -> None:
        self.base_url = os.getenv("AICORE_BASE_URL")
        self.client_id = os.getenv("AICORE_CLIENT_ID")
        self.client_secret = os.getenv("AICORE_CLIENT_SECRET")
        self.resource_group = os.getenv("AICORE_RESOURCE_GROUP", "default")
        self.model = os.getenv("AICORE_MODEL", "gpt-4")
        
        if not all([self.base_url, self.client_id, self.client_secret]):
            raise ValueError("SAP AI Core environment variables not set")
        
        self.access_token: Optional[str] = None
    
    async def _get_access_token(self) -> str:
        """Get OAuth2 access token for SAP AI Core."""
        if self.access_token:
            return self.access_token
        
        # TODO: Implement proper OAuth2 flow for SAP BTP
        # This is a simplified stub - production would need:
        # 1. Token endpoint discovery
        # 2. Client credentials grant
        # 3. Token caching and refresh
        
        async with httpx.AsyncClient() as client:
            # Placeholder - actual implementation would call token endpoint
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()
            self.access_token = result["access_token"]
            return self.access_token
    
    async def score_output(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> dict[str, Any]:
        """Score output using SAP AI Core."""
        token = await self._get_access_token()
        prompt = self._build_scoring_prompt(final_answer, evidence, user_query, constraints)
        
        async with httpx.AsyncClient() as client:
            # TODO: Adjust endpoint and payload format for SAP AI Core
            response = await client.post(
                f"{self.base_url}/v2/inference/deployments/{self.model}/chat/completions",
                headers={
                    "Authorization": f"Bearer {token}",
                    "AI-Resource-Group": self.resource_group,
                },
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    return json.loads(content[start:end].strip())
                raise
    
    def rewrite_with_evidence(
        self,
        original_answer: str,
        evidence: list[str],
        user_query: str,
    ) -> str:
        """Rewrite answer using only evidence."""
        # Synchronous wrapper - in production would use async
        import asyncio
        return asyncio.run(self._rewrite_async(original_answer, evidence, user_query))
    
    async def _rewrite_async(
        self,
        original_answer: str,
        evidence: list[str],
        user_query: str,
    ) -> str:
        """Async rewrite implementation."""
        token = await self._get_access_token()
        prompt = f"""Rewrite using only evidence:

Query: {user_query}
Evidence: {chr(10).join(evidence[:3])}
Original: {original_answer}

Rewritten:"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/inference/deployments/{self.model}/chat/completions",
                headers={
                    "Authorization": f"Bearer {token}",
                    "AI-Resource-Group": self.resource_group,
                },
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _build_scoring_prompt(
        self,
        final_answer: str,
        evidence: list[str],
        user_query: str,
        constraints: list[str],
    ) -> str:
        """Build scoring prompt."""
        return f"""Evaluate output. Return JSON scores (0-1):

Query: {user_query}
Evidence: {chr(10).join(f"[{i+1}] {e[:200]}" for i, e in enumerate(evidence[:5]))}
Output: {final_answer}

JSON:
{{"accuracy_grounding": 0.0, "relevance": 0.0, "constraint_adherence": 0.0, "tone_policy": 0.0}}"""


def get_judge(provider: str) -> Judge:
    """Get a judge instance for the specified provider.
    
    Args:
        provider: One of 'openai', 'anthropic', 'sap'
        
    Returns:
        Judge instance
    """
    if provider == "openai":
        return OpenAIJudge()
    elif provider == "anthropic":
        return AnthropicJudge()
    elif provider == "sap":
        return SAPAICoreJudge()
    else:
        raise ValueError(f"Unknown provider: {provider}")
