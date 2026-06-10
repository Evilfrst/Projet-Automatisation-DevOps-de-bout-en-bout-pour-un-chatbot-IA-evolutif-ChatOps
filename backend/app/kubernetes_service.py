from kubernetes import client, config
from datetime import datetime


def load_cluster():
    """
    Charge la configuration Kubernetes.
    Retourne True si le cluster est disponible,
    False sinon.
    """

    try:
        config.load_incluster_config()
        return True

    except Exception:

        try:
            config.load_kube_config()
            return True

        except Exception:
            return False


def list_pods():

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        v1 = client.CoreV1Api()

        pods = v1.list_pod_for_all_namespaces()

        return [
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase
            }
            for pod in pods.items
        ]

    except Exception as e:
        return {"error": str(e)}


def list_deployments():

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        apps = client.AppsV1Api()

        deployments = apps.list_deployment_for_all_namespaces()

        return [
            {
                "name": dep.metadata.name,
                "namespace": dep.metadata.namespace,
                "replicas": dep.spec.replicas
            }
            for dep in deployments.items
        ]

    except Exception as e:
        return {"error": str(e)}


def list_services():

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        v1 = client.CoreV1Api()

        services = v1.list_service_for_all_namespaces()

        return [
            {
                "name": svc.metadata.name,
                "namespace": svc.metadata.namespace,
                "type": svc.spec.type
            }
            for svc in services.items
        ]

    except Exception as e:
        return {"error": str(e)}


def failed_pods():

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        v1 = client.CoreV1Api()

        pods = v1.list_pod_for_all_namespaces()

        return [
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase
            }
            for pod in pods.items
            if pod.status.phase != "Running"
        ]

    except Exception as e:
        return {"error": str(e)}


def pod_logs(namespace, pod_name):

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        v1 = client.CoreV1Api()

        return v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=100
        )

    except Exception as e:
        return {"error": str(e)}


def restart_deployment(namespace, deployment_name):

    if not load_cluster():
        return {
            "error": "Kubernetes cluster unavailable"
        }

    try:
        apps = client.AppsV1Api()

        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt":
                            datetime.utcnow().isoformat()
                        }
                    }
                }
            }
        }

        apps.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=body
        )

        return {
            "message": f"{deployment_name} redémarré"
        }

    except Exception as e:
        return {"error": str(e)}
