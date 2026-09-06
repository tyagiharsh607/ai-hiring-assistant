import httpx

from app.config import settings

PDL_SEARCH_URL = "https://api.peopledatalabs.com/v5/person/search"


async def search_people(job_title: str, location: str | None, size: int = 10) -> list[dict]:
    """Elasticsearch-style PDL person search, filtered by job title (and optional location)."""
    # job_title is free text (e.g. "backend engineer", "recruiter") - `match` handles it well.
    must = [{"match": {"job_title": job_title}}]
    if location:
        must.append({"match": {"location_name": location}})

    query = {"query": {"bool": {"must": must}}, "size": size}

    headers = {"X-Api-Key": settings.pdl_api_key}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(PDL_SEARCH_URL, headers=headers, json=query)
        # PDL returns HTTP 404 for a genuine "no matches" result, not just a bad URL -
        # treat it as an empty result set instead of an error.
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        body = resp.json()

    def _first_real(value):
        """PDL returns `true` (not the actual value) for contact fields your plan
        doesn't have PII access to, instead of omitting them. Treat non-list values
        as "not actually available" rather than surfacing the placeholder."""
        if isinstance(value, list) and value:
            item = value[0]
            return item.get("address") if isinstance(item, dict) else item
        return None

    results = []
    for person in body.get("data", []):
        results.append(
            {
                "name": person.get("full_name"),
                "title": person.get("job_title"),
                "company": person.get("job_company_name"),
                "email": _first_real(person.get("emails")),
                "phone": _first_real(person.get("phone_numbers")),
                "linkedin_url": person.get("linkedin_url"),
            }
        )
    return results
