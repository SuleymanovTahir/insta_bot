# cache.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_client_cached(client_id):
    return get_client_by_id(client_id)