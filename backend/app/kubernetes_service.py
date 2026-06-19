import os
from datetime import datetime, timezone

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

LAST_K8S_ERROR: str | None = None
REQUEST_TIMEOUT = int(os.getenv("K8S_REQUEST_TIMEOUT", "10"))


def load_cluster() -> bool:
    """Charge la configuration Kubernetes depuis le pod ou un kubeconfig monté."""
    global LAST_K8S_ERROR

    try:
        config.load_incluster_config()
        LAST_K8S_ERROR = None
        return True
    except Exception as incluster_error:
        try:
            kubeconfig_path = os.getenv("KUBECONFIG", "/root/.kube/config")
            config.load_kube_config(config_file=kubeconfig_path)
            LAST_K8S_ERROR = None
            return True
        except Exception as kubeconfig_error:
            LAST_K8S_ERROR = (
                f"in-cluster: {incluster_error}; " f"kubeconfig: {kubeconfig_error}"
            )
            return False


def cluster_unavailable_response() -> dict:
    return {
        "error": "Kubernetes cluster unavailable",
        "detail": LAST_K8S_ERROR,
    }


def _api_error(exc: Exception) -> dict:
    if isinstance(exc, ApiException):
        return {
            "error": "Kubernetes API error",
            "status": exc.status,
            "reason": exc.reason,
            "detail": exc.body,
        }
    return {"error": "Kubernetes request failed", "detail": str(exc)}


def list_pods() -> list[dict] | dict:
    if not load_cluster():
        return cluster_unavailable_response()

    try:
        pods = client.CoreV1Api().list_pod_for_all_namespaces(
            _request_timeout=REQUEST_TIMEOUT
        )
        return [
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "node": pod.spec.node_name,
            }
            for pod in pods.items
        ]
    except Exception as exc:
        return _api_error(exc)


def list_deployments() -> list[dict] | dict:
    if not load_cluster():
        return cluster_unavailable_response()

    try:
        deployments = client.AppsV1Api().list_deployment_for_all_namespaces(
            _request_timeout=REQUEST_TIMEOUT
        )
        return [
            {
                "name": dep.metadata.name,
                "namespace": dep.metadata.namespace,
                "replicas": dep.spec.replicas or 0,
                "available_replicas": dep.status.available_replicas or 0,
            }
            for dep in deployments.items
        ]
    except Exception as exc:
        return _api_error(exc)


def list_services() -> list[dict] | dict:
    if not load_cluster():
        return cluster_unavailable_response()

    try:
        services = client.CoreV1Api().list_service_for_all_namespaces(
            _request_timeout=REQUEST_TIMEOUT
        )
        return [
            {
                "name": svc.metadata.name,
                "namespace": svc.metadata.namespace,
                "type": svc.spec.type,
                "cluster_ip": svc.spec.cluster_ip,
            }
            for svc in services.items
        ]
    except Exception as exc:
        return _api_error(exc)


def failed_pods() -> list[dict] | dict:
    pods = list_pods()
    if not isinstance(pods, list):
        return pods
    return [pod for pod in pods if pod["status"] not in {"Running", "Succeeded"}]


def pod_logs(namespace: str, pod_name: str) -> str | dict:
    if not load_cluster():
        return cluster_unavailable_response()

    try:
        return client.CoreV1Api().read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=100,
            timestamps=True,
            _request_timeout=REQUEST_TIMEOUT,
        )
    except Exception as exc:
        return _api_error(exc)


def restart_deployment(namespace: str, deployment_name: str) -> dict:
    if not load_cluster():
        return cluster_unavailable_response()

    try:
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": datetime.now(
                                timezone.utc
                            ).isoformat()
                        }
                    }
                }
            }
        }
        client.AppsV1Api().patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=body,
            _request_timeout=REQUEST_TIMEOUT,
        )
        return {"message": f"Deployment {namespace}/{deployment_name} redémarré"}
    except Exception as exc:
        return _api_error(exc)
