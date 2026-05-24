import subprocess


class SSHTunnel:
    def __init__(self, local_port, remote_port, host, user, name, registry=None):
        self.local_port = local_port
        self.remote_port = remote_port
        self.host = host
        self.user = user
        self.name = name
        self.registry = registry
        self.process = None

    def start(self):
        cmd = [
            "ssh",
            "-N",
            "-L",
            f"{self.local_port}:localhost:{self.remote_port}",
            f"{self.user}@{self.host}"
        ]

        self.process = subprocess.Popen(cmd)

        if self.registry:
            self.registry.register(self.name, self)

        return self.process

    def is_alive(self):
        result = subprocess.run([
            "ssh",
            f"{self.user}@{self.host}",
            "pgrep -f 'ssh.*{self.remote_port}'"
        ], capture_output=True, text=True)

        return bool(result.stdout.strip())

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except:
                self.process.kill()

        if self.registry:
            self.registry.unregister(self.name)