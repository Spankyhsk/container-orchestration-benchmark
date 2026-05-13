def compare_scores(docker_score, kubernetes_score):

    if docker_score > kubernetes_score:
        return "Docker performed better"

    elif kubernetes_score > docker_score:
        return "Kubernetes performed better"

    return "Both environments performed equally"