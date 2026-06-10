import requests
import os

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://prometheus:9090"
)

def query_prometheus(query: str):

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={
            "query": query
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def cluster_health():

    return query_prometheus("up")
