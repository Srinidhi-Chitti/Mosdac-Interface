def classify_query(query: str) -> str:
    query = query.lower()
    if "solve" in query or "trajectory" in query:
        return "solve_equation"
    elif "equation" in query and "mission" in query:
        return "mission_equation"
    elif "research" in query or "paper" in query:
        return "research_query"
    else:
        return "rag_fallback"