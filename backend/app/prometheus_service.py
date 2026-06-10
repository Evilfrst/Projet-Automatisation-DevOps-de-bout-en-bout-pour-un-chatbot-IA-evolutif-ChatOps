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

def cpu_usage():

    return query_prometheus(
        '100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    )


def memory_usage():

    return query_prometheus(
        '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))*100'
    )


def pod_count():

    return query_prometheus(
        'count(kube_pod_info)'
    )
