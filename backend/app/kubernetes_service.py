from kubernetes import client, config

def load_cluster():

    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()

def list_pods():

    load_cluster()

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

def list_deployments():

    load_cluster()

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

def list_services():

    load_cluster()

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

def failed_pods():

    load_cluster()

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

def pod_logs(namespace, pod_name):

    load_cluster()

    v1 = client.CoreV1Api()

    return v1.read_namespaced_pod_log(
        name=pod_name,
        namespace=namespace,
        tail_lines=100
    )

from datetime import datetime

def restart_deployment(
    namespace,
    deployment_name
):

    load_cluster()

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
