import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("kubernetes-copilot.mcp")

# Official Kubernetes Documentation Knowledge Registry
# Covers the core categories: Concepts, Tasks, Reference, Troubleshooting, Workloads, Networking, Storage, Security
K8S_DOCS_REGISTRY: List[Dict[str, Any]] = [
    {
        "document_id": "k8s-overview-what-is",
        "title": "What is Kubernetes? (Overview & Business Benefits)",
        "section": "Concepts > Overview > What is Kubernetes?",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/overview/",
        "keywords": ["roi", "business", "benefits", "virtual machines", "vms", "containers", "overview", "cost", "cloud", "why use kubernetes"],
        "summary": "Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services. It provides automated self-healing, bin packing for cost savings, service discovery, and zero-downtime rollouts compared to traditional virtual machines.",
        "content": (
            "Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services, "
            "that facilitates both declarative configuration and automation.\n\n"
            "Why do organizations need Kubernetes and what are its key business benefits over traditional Virtual Machines (VMs)?\n"
            "1. Evolution from VMs to Containers:\n"
            "   - Traditional Era: Applications ran on physical servers without resource boundaries.\n"
            "   - Virtualization Era: Virtual Machines (VMs) ran multiple OS instances on a single physical CPU. However, each VM requires a full OS stack, consuming heavy memory and license overhead.\n"
            "   - Container Era: Containers share the underlying operating system (OS) kernel across applications. They are lightweight, start in seconds, and maximize hardware utilization.\n\n"
            "2. Direct Business & ROI Value of Kubernetes:\n"
            "   - Service discovery and load balancing: Exposes containers using their own IP addresses or DNS names and distributes network traffic to keep apps stable under heavy traffic.\n"
            "   - Storage orchestration: Automatically mounts cloud storage systems (AWS EBS, Google Persistent Disk, Azure Disk, local storage).\n"
            "   - Automated rollouts and rollbacks: Deploy new features safely with zero downtime. If an update fails, Kubernetes automatically rolls back to the previous stable release.\n"
            "   - Automatic bin packing (Cloud Cost Reduction): You specify CPU and memory budgets for each container. Kubernetes automatically packs containers onto nodes to optimize server efficiency and reduce monthly cloud bills.\n"
            "   - Self-healing & High Availability: Restarts failed containers, replaces unhealthy containers, kills containers that don't respond to user-defined health checks, and doesn't advertise them to clients until ready.\n"
            "   - Secret and configuration management: Securely stores sensitive information (passwords, tokens, SSH keys) without rebuilding container images or exposing secrets in code."
        )
    },
    {
        "document_id": "k8s-pod",
        "title": "Pods",
        "section": "Concepts > Workloads > Pods",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/workloads/pods/",
        "keywords": ["pod", "container", "workload", "lifecycle", "spec", "manifest"],
        "summary": "Pods are the smallest deployable units of computing that you can create and manage in Kubernetes. A Pod contains one or more containers with shared storage and network resources.",
        "content": (
            "Pods are the smallest deployable units of computing that you can create and manage in Kubernetes.\n"
            "A Pod is a group of one or more containers, with shared storage and network resources, and a specification for how to run the containers.\n"
            "A Pod's contents are always co-located and co-scheduled, and run in a shared context. A Pod models an application-specific 'logical host': "
            "it contains one or more application containers which are relatively tightly coupled.\n"
            "Pod lifecycle phases include: Pending, Running, Succeeded, Failed, and Unknown.\n"
            "Official kubectl commands:\n"
            "- kubectl get pods -o wide\n"
            "- kubectl describe pod <pod-name>\n"
            "- kubectl logs <pod-name> -c <container-name>\n"
            "- kubectl delete pod <pod-name>"
        )
    },
    {
        "document_id": "k8s-deployment",
        "title": "Deployments",
        "section": "Concepts > Workloads > Controllers",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/",
        "keywords": ["deployment", "rollout", "replicaset", "scaling", "rolling update", "declarative"],
        "summary": "A Deployment provides declarative updates for Pods and ReplicaSets. You describe a desired state in a Deployment, and the Deployment Controller changes the actual state to the desired state.",
        "content": (
            "A Deployment provides declarative updates for Pods and ReplicaSets.\n"
            "You describe a desired state in a Deployment, and the Deployment Controller changes the actual state to the desired state at a controlled rate.\n"
            "You can define Deployments to create new ReplicaSets, or to remove existing Deployments and adopt all their resources with new Deployments.\n"
            "Common use cases:\n"
            "1. Create a Deployment to rollout a ReplicaSet.\n"
            "2. Declare the new state of the Pods by updating the PodTemplateSpec of the Deployment.\n"
            "3. Rollback to an earlier Deployment revision if current state is unstable.\n"
            "4. Scale up the Deployment to facilitate more load.\n"
            "5. Pause the rollout of a Deployment to apply multiple fixes and resume it.\n"
            "Official kubectl commands:\n"
            "- kubectl apply -f deployment.yaml\n"
            "- kubectl rollout status deployment/<deployment-name>\n"
            "- kubectl rollout undo deployment/<deployment-name>\n"
            "- kubectl scale deployment/<deployment-name> --replicas=5"
        )
    },
    {
        "document_id": "k8s-service",
        "title": "Services",
        "section": "Concepts > Services, Load Balancing, and Networking",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/services-networking/service/",
        "keywords": ["service", "clusterip", "nodeport", "loadbalancer", "endpoints", "kube-proxy", "dns"],
        "summary": "An abstract way to expose an application running on a set of Pods as a network service with a stable IP and DNS name.",
        "content": (
            "In Kubernetes, a Service is a method for exposing a network application that is running as one or more Pods in your cluster.\n"
            "The set of Pods targeted by a Service is usually determined by a selector (.spec.selector).\n"
            "Service Types:\n"
            "1. ClusterIP: Exposes the Service on a cluster-internal IP (default). Choosing this value makes the Service only reachable from within the cluster.\n"
            "2. NodePort: Exposes the Service on each Node's IP at a static port (the NodePort). You'll be able to contact the NodePort Service from outside the cluster.\n"
            "3. LoadBalancer: Exposes the Service externally using an external cloud provider's load balancer.\n"
            "4. ExternalName: Maps the Service to the contents of the externalName field (e.g. foo.bar.example.com) by returning a CNAME record.\n"
            "Official kubectl commands:\n"
            "- kubectl get svc\n"
            "- kubectl describe svc <service-name>\n"
            "- kubectl expose deployment <deployment-name> --port=80 --target-port=8080"
        )
    },
    {
        "document_id": "k8s-ingress",
        "title": "Ingress",
        "section": "Concepts > Services, Load Balancing, and Networking",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/services-networking/ingress/",
        "keywords": ["ingress", "routing", "http", "https", "tls", "load balancing", "reverse proxy"],
        "summary": "Ingress exposes HTTP and HTTPS routes from outside the cluster to services within the cluster. Traffic routing is controlled by rules defined on the Ingress resource.",
        "content": (
            "Ingress exposes HTTP and HTTPS routes from outside the cluster to services within the cluster. "
            "Traffic routing is controlled by rules defined on the Ingress resource.\n"
            "An Ingress may be configured to give Services externally-reachable URLs, load balance traffic, terminate SSL/TLS, and offer name-based virtual hosting.\n"
            "An Ingress controller is responsible for fulfilling the Ingress, usually with a load balancer, though it may also configure your edge router or additional frontends.\n"
            "Official kubectl commands:\n"
            "- kubectl get ingress\n"
            "- kubectl describe ingress <ingress-name>"
        )
    },
    {
        "document_id": "k8s-troubleshooting-crashloop",
        "title": "Troubleshooting Applications & CrashLoopBackOff",
        "section": "Tasks > Monitoring, Logging, and Debugging",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/",
        "keywords": ["crashloopbackoff", "troubleshooting", "debug", "exit code", "restart", "logs", "describe"],
        "summary": "CrashLoopBackOff indicates that a container repeatedly crashes and restarts with exponential backoff delay. Debug using kubectl describe and kubectl logs.",
        "content": (
            "CrashLoopBackOff is a Pod status indicating that one or more containers in a Pod are repeatedly failing, crashing, or exiting abnormally.\n"
            "Kubernetes applies an exponential backoff delay (10s, 20s, 40s... up to 5 minutes) between restart attempts.\n"
            "Official Kubernetes Diagnostic Steps:\n"
            "1. Inspect Pod Status & Exit Code:\n"
            "   kubectl describe pod <pod-name>\n"
            "   Look at the 'Last State' and 'Exit Code' (e.g., Exit Code 1 = Application error, Exit Code 137 = OOMKilled/SIGKILL, Exit Code 139 = Segfault).\n"
            "2. Inspect Container Application Logs:\n"
            "   kubectl logs <pod-name> -c <container-name>\n"
            "3. Check Previous Crashed Instance Logs:\n"
            "   kubectl logs <pod-name> -c <container-name> --previous\n"
            "4. Check Liveness / Readiness Probes:\n"
            "   Misconfigured health checks failing repeatedly will trigger container restarts.\n"
            "5. Common Root Causes:\n"
            "   - Missing environment variables, ConfigMaps, or Secrets.\n"
            "   - Application configuration or file permission errors.\n"
            "   - Insufficient memory leading to OOMKilled.\n"
            "   - Failing startup/liveness probe thresholds."
        )
    },
    {
        "document_id": "k8s-troubleshooting-imagepull",
        "title": "Troubleshooting ImagePullBackOff and ErrImagePull",
        "section": "Tasks > Monitoring, Logging, and Debugging",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/containers/images/",
        "keywords": ["imagepullbackoff", "errimagepull", "docker", "registry", "imagepullsecrets"],
        "summary": "ImagePullBackOff indicates that Kubernetes cannot retrieve the container image from the container registry. Debug registry authentication, image tag, and network connectivity.",
        "content": (
            "ImagePullBackOff occurs when the kubelet fails to pull the specified container image from the registry.\n"
            "Common Causes:\n"
            "1. Incorrect image name or non-existent tag (e.g. 404 Not Found from registry).\n"
            "2. Missing or incorrect imagePullSecrets for private registry authentication.\n"
            "3. Network reachability issues between the Kubernetes worker node and the container registry.\n"
            "4. Docker Hub rate limiting (HTTP 429 Too Many Requests).\n"
            "Official Troubleshooting Steps:\n"
            "kubectl describe pod <pod-name>\n"
            "Check the 'Events' section at the bottom for detailed pull failure messages."
        )
    },
    {
        "document_id": "k8s-configmap-secrets",
        "title": "ConfigMaps and Secrets",
        "section": "Concepts > Configuration",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/configuration/configmap/",
        "keywords": ["configmap", "secret", "configuration", "environment", "volume", "base64"],
        "summary": "ConfigMaps and Secrets decouple environment-specific configuration and confidential data from container images.",
        "content": (
            "A ConfigMap is an API object used to store non-confidential data in key-value pairs. Pods can consume ConfigMaps as environment variables, command-line arguments, or as configuration files in a Volume.\n"
            "A Secret is an object that contains a small amount of sensitive data such as a password, a token, or a key.\n"
            "Using Secrets means that you don't need to include confidential data in your application code.\n"
            "Official kubectl commands:\n"
            "- kubectl create configmap my-config --from-literal=key=value\n"
            "- kubectl create secret generic my-secret --from-literal=password=secret123\n"
            "- kubectl get configmaps,secrets"
        )
    },
    {
        "document_id": "k8s-statefulset",
        "title": "StatefulSets",
        "section": "Concepts > Workloads > Controllers",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/",
        "keywords": ["statefulset", "stateful", "persistent storage", "ordinal", "headless service"],
        "summary": "StatefulSet manages the deployment and scaling of a set of Pods, and provides guarantees about the ordering and uniqueness of these Pods.",
        "content": (
            "StatefulSet is the workload API object used to manage stateful applications.\n"
            "Unlike a Deployment, a StatefulSet maintains a sticky identity for each of their Pods. These pods are created from the same spec, but are not interchangeable: each has a persistent identifier that it maintains across any rescheduling.\n"
            "Key Features:\n"
            "1. Stable, unique network identifiers (e.g. web-0, web-1) using Headless Services.\n"
            "2. Stable, persistent storage mapped via volumeClaimTemplates.\n"
            "3. Ordered, graceful deployment and scaling.\n"
            "4. Ordered, automated rolling updates."
        )
    },
    {
        "document_id": "k8s-daemonset",
        "title": "DaemonSets",
        "section": "Concepts > Workloads > Controllers",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/",
        "keywords": ["daemonset", "node", "logging", "monitoring", "cni", "kube-proxy"],
        "summary": "A DaemonSet ensures that all (or some) Nodes run a copy of a Pod. As nodes are added to the cluster, Pods are added to them.",
        "content": (
            "A DaemonSet ensures that all (or some) Nodes run a copy of a Pod. As nodes are added to the cluster, Pods are added to them. As nodes are removed from the cluster, those Pods are garbage collected.\n"
            "Typical use cases:\n"
            "1. Running a cluster storage daemon on every node (e.g., ceph, glusterd).\n"
            "2. Running a logs collection daemon on every node (e.g., Fluentd, Logstash).\n"
            "3. Running a node monitoring daemon on every node (e.g., Prometheus Node Exporter, datadog-agent)."
        )
    },
    {
        "document_id": "k8s-architecture",
        "title": "Kubernetes Architecture & Components",
        "section": "Concepts > Overview > Components",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/concepts/overview/components/",
        "keywords": ["architecture", "control plane", "kube-apiserver", "etcd", "kube-scheduler", "kube-controller-manager", "kubelet", "kube-proxy"],
        "summary": "Kubernetes cluster consists of Control Plane components (kube-apiserver, etcd, kube-scheduler, kube-controller-manager) and Node components (kubelet, kube-proxy, container runtime).",
        "content": (
            "A Kubernetes cluster consists of two main layers:\n"
            "1. Control Plane Components:\n"
            "   - kube-apiserver: Exposes the Kubernetes API; the front end for the control plane.\n"
            "   - etcd: Consistent and highly-available key value store for all cluster data.\n"
            "   - kube-scheduler: Watches for newly created Pods with no assigned node, and selects a node for them to run on.\n"
            "   - kube-controller-manager: Runs controller processes (Node controller, Job controller, EndpointSlice controller, ServiceAccount controller).\n"
            "   - cloud-controller-manager: Embeds cloud-specific control logic.\n"
            "2. Node Components:\n"
            "   - kubelet: An agent that runs on each node in the cluster. It makes sure that containers are running in a Pod.\n"
            "   - kube-proxy: A network proxy that runs on each node, maintaining network rules on nodes allowing network communication to your Pods.\n"
            "   - Container runtime: The software that is responsible for running containers (e.g. containerd, CRI-O)."
        )
    },
    {
        "document_id": "k8s-kubectl-cheatsheet",
        "title": "kubectl Quick Reference & Cheat Sheet",
        "section": "Reference > kubectl CLI",
        "source": "Kubernetes Official Documentation",
        "url": "https://kubernetes.io/docs/reference/kubectl/quick-reference/",
        "keywords": ["kubectl", "cli", "cheat sheet", "commands", "syntax", "flags"],
        "summary": "Official reference of commonly used kubectl commands for viewing, creating, updating, and debugging cluster resources.",
        "content": (
            "Official kubectl syntax:\n"
            "kubectl [command] [TYPE] [NAME] [flags]\n\n"
            "Core commands:\n"
            "- kubectl get pods -A : List all pods across all namespaces\n"
            "- kubectl get nodes : Check cluster node status\n"
            "- kubectl describe pod <name> : Show detailed pod events and state\n"
            "- kubectl logs -f <name> : Stream container logs\n"
            "- kubectl exec -it <name> -- /bin/sh : Run interactive shell inside container\n"
            "- kubectl top pods / nodes : Check CPU and memory usage (requires metrics-server)\n"
            "- kubectl port-forward pod/<name> 8080:80 : Forward local port to pod"
        )
    }
]

class KubernetesDocsMCPClient:
    """
    Kubernetes Documentation Model Context Protocol (MCP) Client.
    Provides standard tools to search, look up, and retrieve official
    Kubernetes documentation without interacting with live clusters.
    """
    def __init__(self, registry: Optional[List[Dict[str, Any]]] = None):
        self.registry = registry or K8S_DOCS_REGISTRY
        logger.info(f"Initialized KubernetesDocsMCPClient with {len(self.registry)} official documentation resources.")

    def search_docs(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Search official documentation by matching terms against title, keywords, section, and summary.
        """
        query_tokens = [t.lower() for t in query.replace("-", " ").split() if len(t) > 2]
        scored_docs = []

        for doc in self.registry:
            score = 0
            doc_text = f"{doc['title']} {doc['section']} {doc['summary']} {' '.join(doc['keywords'])}".lower()
            
            for token in query_tokens:
                if token in doc["title"].lower():
                    score += 5
                elif any(token in kw.lower() for kw in doc["keywords"]):
                    score += 3
                elif token in doc_text:
                    score += 1
            
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [doc for _, doc in scored_docs[:limit]]
        
        # If no strict keyword matches, return most relevant general overview
        if not results and self.registry:
            results = self.registry[:limit]

        return results

    def get_doc_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Direct lookup of a documentation page by its official document_id.
        """
        for doc in self.registry:
            if doc["document_id"] == document_id:
                return doc
        return None

    def get_doc_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Lookup official documentation entry by URL.
        """
        for doc in self.registry:
            if doc["url"] == url:
                return doc
        return None

    def list_categories(self) -> List[str]:
        """
        Returns all unique official documentation categories.
        """
        return sorted(list(set(doc["section"].split(" > ")[0] for doc in self.registry)))

# Global MCP Client instance
mcp_client = KubernetesDocsMCPClient()
