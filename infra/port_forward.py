import subprocess


class PortForward:
    def __init__(self, name, host, user, services, registry=None):
        """
        services:
        [
            {"name": "grafana", "service": "monitoring-grafana"},
            {"name": "prometheus", "service": "monitoring-kube-prometheus-prometheus"}
        ]
        """
        self.name = name
        self.host = host
        self.user = user
        self.services = services
        self.registry = registry

    # =====================================================
    # START (VM script einmalig)
    # =====================================================
    def start(self):
        subprocess.run([
            "ssh",
            f"{self.user}@{self.host}",
            "bash ~/bench-control/start_portforwards.sh"
        ])

        if self.registry:
            self.registry.register(self.name, self)

    # =====================================================
    # STOP (VM script einmalig)
    # =====================================================
    def stop(self):
        subprocess.run([
            "ssh",
            f"{self.user}@{self.host}",
            "bash ~/bench-control/stop_portforwards.sh"
        ])

        if self.registry:
            self.registry.unregister(self.name)

    # =====================================================
    # VARIANTE B: RETURN DICT (pro service status)
    # =====================================================
    def is_alive(self):
        status = {}

        for s in self.services:
            cmd = [
                "ssh",
                f"{self.user}@{self.host}",
                f"pgrep -f 'kubectl port-forward.*{s['service']}'"
            ]

            res = subprocess.run(cmd, capture_output=True, text=True)

            status[s["name"]] = bool(res.stdout.strip())

        return status