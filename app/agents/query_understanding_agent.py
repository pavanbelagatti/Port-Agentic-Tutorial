from __future__ import annotations

import re
from typing import Any, Dict, List

from app.agents.base import Agent


class QueryUnderstandingAgent(Agent):
    name = "query-understanding-agent"

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower().strip()

        # normalize curly apostrophes and quotes
        text = text.replace("’", "'").replace("“", '"').replace("”", '"')

        # keep hyphenated service names like slack-app
        tokens = re.findall(r"[a-zA-Z0-9_-]+", text)
        return tokens

    def _extract_candidate(self, query: str) -> str:
        original = query.strip()
        lowered = original.lower()

        # if query is already a likely service identifier, return it as-is
        if re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", original):
            return original

        tokens = self._tokenize(lowered)

        stopwords = {
            "what", "whats", "what's", "going", "on", "with", "is", "the", "a", "an",
            "analyze", "check", "tell", "me", "about", "status", "of", "for", "please",
            "service", "services", "do", "does", "how", "look", "looks", "healthy",
            "health", "show", "give", "details"
        }

        filtered = [t for t in tokens if t not in stopwords]

        # prefer hyphenated / service-like tokens
        ranked: List[str] = []
        for token in filtered:
            score = 0
            if "-" in token:
                score += 5
            if token.endswith("service"):
                score += 3
            if token.endswith("app"):
                score += 3
            if token.endswith("worker"):
                score += 2
            if token.startswith("port"):
                score += 1
            if token.startswith("lakehouse"):
                score += 1
            ranked.append((score, token))

        if ranked:
            ranked.sort(reverse=True)
            return ranked[0][1]

        if filtered:
            return filtered[-1]

        return original

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        original_query = state["query"]
        extracted = self._extract_candidate(original_query)

        state["original_query"] = original_query
        state["query"] = extracted
        state["trace"].append(
            f"{self.name}: extracted service candidate '{extracted}' from '{original_query}'"
        )
        return state