import psutil


def cleanup_processes(names):
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])

            for name in names:
                if name in cmdline:
                    proc.kill()

        except Exception:
            pass