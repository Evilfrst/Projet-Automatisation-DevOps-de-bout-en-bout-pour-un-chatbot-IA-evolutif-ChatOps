import math
import os

import requests


PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://prometheus:9090",
)


def query_prometheus(query: str) -> dict:
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def extract_scalar(
    prometheus_response: dict,
    default: float = 0.0,
) -> float:
    """
    Extrait une valeur numérique d'une réponse de l'API Prometheus.

    Prend en charge les résultats de type vector et scalar.
    Retourne `default` si aucune valeur exploitable n'est disponible.
    """
    try:
        if prometheus_response.get("status") != "success":
            return default

        data = prometheus_response.get("data", {})
        result_type = data.get("resultType")
        result = data.get("result")

        if result_type == "vector":
            if not result:
                return default

            value = float(result[0]["value"][1])

        elif result_type == "scalar":
            if not result or len(result) < 2:
                return default

            value = float(result[1])

        else:
            return default

        if not math.isfinite(value):
            return default

        return value

    except (KeyError, IndexError, TypeError, ValueError):
        return default


def cluster_health() -> dict:
    return query_prometheus("up")


def cpu_usage() -> dict:
    return query_prometheus(
        '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    )


def memory_usage() -> dict:
    return query_prometheus(
        """
        (1 - (
            node_memory_MemAvailable_bytes
            /
            node_memory_MemTotal_bytes
        )) * 100
        """
    )


def pod_count() -> dict:
    return query_prometheus(
        'count(kube_pod_status_phase{phase="Running"})'
    )
