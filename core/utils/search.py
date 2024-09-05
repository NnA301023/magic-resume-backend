from typing import List, Optional, Dict


def search_similar_jobs(
    client: object, 
    title: str, skill: List[str], 
    location: Optional[str], max_result: int = 5
    ) -> List[Dict[str, str]]:
    
    skill = " ".join(skill)
    params = {
        "q": f"{title} {skill} {location}",
        "query_by": "title,description,location"
    }
    result = client.documents.search(params)

    filter_result = []
    for _doc in result["hits"]:
        if len(filter_result) == max_result:
            break
        doc = _doc["document"]
        doc.pop("id", None)
        filter_result.append(doc)

    return filter_result