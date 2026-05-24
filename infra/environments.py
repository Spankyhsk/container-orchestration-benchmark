import subprocess

from infra.ssh_manager import SSHTunnel
from infra.port_forward import PortForward


class DockerEnvironment:

    def __init__(self, config: dict):
        self.config = config
        self.host = config.get("SSH_HOST")
        self.user = config.get("SSH_USER")

        self.tunnels = []

    def start(self, registry=None):

        print("[Docker] starting tunnels...")

        grafana = SSHTunnel(
            local_port=3002,
            remote_port=3000,
            host=self.host,
            user=self.user,
            name="ssh-docker-grafana",
            registry=registry
        )

        prom = SSHTunnel(
            local_port=9090,
            remote_port=9090,
            host=self.host,
            user=self.user,
            name="ssh-docker-prom",
            registry=registry
        )

        grafana.start()
        prom.start()

        self.tunnels = [grafana, prom]

    def stop(self):
        print("[Docker] stopping tunnels...")
        for t in self.tunnels:
            t.stop()


# =========================================================
# K3S
# =========================================================

class K3sEnvironment:

    def __init__(self, config: dict):
        self.config = config
        self.host = config["SSH_HOST"]
        self.user = config["SSH_USER"]

        self.vm_processes = []
        self.tunnels = []

    def _cleanup_vm_portforwards(self):
        subprocess.run([
            "ssh",
            f"{self.user}@{self.host}",
            "pkill -f 'kubectl port-forward' || true"
        ])

    def start(self, registry=None):

        print("[K3s] cleaning VM state BEFORE starting...")
        self._cleanup_vm_portforwards()

        services = [
            {"name": "grafana", "service": "monitoring-grafana"},
            {"name": "prom", "service": "monitoring-kube-prometheus-prometheus"}
        ]

        pf = PortForward(
            host=self.host,
            user=self.user,
            name="pf-k3s",
            services=services,
            registry=registry
        )

        pf.start()
        self.vm_processes = [pf]

        grafana = SSHTunnel(
            host=self.host,
            user=self.user,
            local_port=3001,
            remote_port=3000,
            name="ssh-k3s-grafana",
            registry=registry
        )

        prom = SSHTunnel(
            host=self.host,
            user=self.user,
            local_port=9091,
            remote_port=9090,
            name="ssh-k3s-prom",
            registry=registry
        )

        grafana.start()
        prom.start()

        self.tunnels = [grafana, prom]

    def stop(self):
        print("[K3s] stopping everything...")

        for t in self.tunnels:
            t.stop()

        for p in self.vm_processes:
            p.stop()