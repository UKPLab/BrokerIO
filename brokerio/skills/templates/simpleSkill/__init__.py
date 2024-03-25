def create_docker(path, nocache=False):
    """
    Build the docker container
    :param path: path for the Dockerfile
    :param nocache: Do not use cache
    :return: build successful
    """
    # Create a Docker client
    import docker
    client = docker.from_env()

    try:
        build_logs = client.api.build(
            dockerfile="./brokerio/skills/templates/simpleSkill/Dockerfile",
            path=path,
            tag="broker_simple_skill",
            decode=True, rm=True,
            nocache=nocache,
        )

        # Print build output in real-time
        for chunk in build_logs:
            if 'stream' in chunk:
                for line in chunk['stream'].splitlines():
                    print(line)

        # Make sure the build was successful
        for chunk in build_logs:
            if 'error' in chunk:
                print("Failed to build Docker image:", chunk['error'])
                return False

        return True
    except docker.errors.BuildError as e:
        print("Failed to build Docker image:", e)
        return False
