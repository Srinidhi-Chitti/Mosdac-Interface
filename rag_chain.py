from neo4j_tool import CypherTool
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class RagPipeline:
    def __init__(self):
        self.db = CypherTool()

    @lru_cache(maxsize=128)
    def retrieve_context(self, query: str):
        result = self.db.query_neo4j("""
            MATCH (r:ResearchPaper)
            WHERE r.title CONTAINS $query OR r.abstract CONTAINS $query
            RETURN r.title, r.abstract, r.url
            LIMIT 3
        """, {"query": query})

        if not result:
            return "No related research found."

        return "\n\n".join([f"{r['title']} - {r['url']}\n{r['abstract']}" for r in result])
