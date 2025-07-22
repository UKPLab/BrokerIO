"""
This is a simple skill template for building the container of a model.

Author: Dennis Zyska
"""
import inspect
import os
import pathlib

from brokerio.cli import CLI, Colors
from . import load_config
from .templates.simpleSkill import create_docker as build_simple_skill


class SkillModel(CLI):
    def __init__(self, parser, args):
        super().__init__(parser)
        self.parser = parser
        self.args = args
        self.config = self.get_config()

    def get_config(self):
        """
        Get current config of this skill
        :return:
        """
        return load_config(os.path.join(self.args.skill_dir, self.args.skill_name))

    @staticmethod
    def arg_parser(parser):
        """
        Define additional arguments
        :param parser:
        :return:
        """
        pass

    def build(self, build_skill=True):
        """
        Build the docker container
        :param build_skill: Build the skill docker template
        :return:
        """
        import docker
        if 'template' not in self.config or self.config['template'] is None:
            print(Colors.FAIL + "No template defined in config ... end without building..." + Colors.ENDC)
        elif self.config['template'] == "simpleSkill":
            print("path to broker")
            print(pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent.parent.parent)
            path_to_broker = str(pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent.parent.parent)

            # build basic template
            if not build_simple_skill(path_to_broker, nocache=self.args.nocache):
                print(Colors.FAIL + "Failed to build Docker image ... end without building..." + Colors.ENDC)
                return

            # add individual template
            if build_skill:
                client = docker.from_env()

                try:
                    build_logs = client.api.build(
                        dockerfile="Dockerfile",
                        path=str(os.path.join(self.args.skill_dir, self.args.skill_name)),
                        tag=self.config['tag'],
                        decode=True, rm=True,
                        nocache=self.args.nocache,
                    )
                    # Print build output in real-time
                    for chunk in build_logs:
                        if 'stream' in chunk:
                            for line in chunk['stream'].splitlines():
                                print(line)
                except docker.errors.BuildError as e:
                    print("Failed to build Docker image:", e)


        else:
            print(Colors.FAIL + "Unknown template {} ... end without building...".format(
                self.config['template']) + Colors.ENDC)

    def run(self, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter: Additional parameters for the container
        :return: name of containers
        """
        import docker
        # set additional environment parameters
        if additional_parameter is None:
            additional_parameter = {}
        if "environment" not in additional_parameter:
            additional_parameter["environment"] = {}
        if 'SKILL_NAME' not in additional_parameter["environment"]:
            additional_parameter["environment"]['SKILL_NAME'] = self.config[
                'name'] if self.args.skill == "" else self.args.skill
        if 'BROKER_URL' not in additional_parameter["environment"]:
            additional_parameter["environment"]['BROKER_URL'] = self.args.url

        # Check if the container is already built
        client = docker.from_env()
        containers = []
        try:
            print("Running skill {}".format(self.config['name']))

            image = client.images.get(self.config['tag'])
            print("Found image {}".format(image.short_id))

            print("Stop currently running containers...")
            self.stop()

            print("Check network exists...")
            network = {}
            try:
                net = client.networks.get(self.args.network)
                if net:
                    network = {'network': self.args.network}
            except docker.errors.NotFound:
                print("Network not found.")
            except docker.errors.APIError as e:
                print("Error while getting network")
                print(e)

            # Run the container
            for i in range(1, self.args.num_containers + 1):
                c_name = "{}_{}".format(self.config['tag'],
                                        i) if self.args.container_suffix == "" else "{}_{}_{}".format(
                    self.tag,
                    self.args.container_suffix,
                    i)
                # add container name to environment
                if "environment" in additional_parameter:
                    additional_parameter["environment"]["CONTAINER_NAME"] = c_name
                else:
                    additional_parameter["environment"] = {
                        'CONTAINER_NAME': c_name
                    }

                container = client.containers.run(
                    self.config['tag'],
                    name=c_name,
                    detach=True,
                    command='python3 /app/connect.py',
                    restart_policy={"Name": "always"},
                    **additional_parameter,
                    **network
                )
                print(Colors.OKGREEN + "Start container {}".format(container.short_id) + Colors.ENDC)
                print(container.logs().decode('utf-8'))
                containers.append({
                    "name": container.name,
                    "id": container.short_id
                })
                return containers

        except docker.errors.ImageNotFound:
            print("Image not found. Please build the container first.")
            exit()

    def stop(self):
        """
        Stop the skill
        :return: list of stopped containers
        """
        import docker
        stopped_containers = []
        containers = self.get_containers()
        if self.args.container_suffix != "":
            containers = [container for container in containers if
                          container.name.removeprefix("{}_".format(self.tag)).startswith(self.args.container_suffix)]
        for container in containers:
            # check if running
            if container.status != "running":
                continue
            try:
                container.stop(timeout=self.args.timeout if "timeout" in self.args else 10)
                container.wait()
            except docker.errors.APIError:
                container.kill()
            print("Stopped container {}".format(container.name))

        if "only_stop" not in self.args or not self.args.only_stop:
            for container in containers:
                container.remove(force=True)
                print("Removed container {}".format(container.name))
                if container.name not in stopped_containers:
                    stopped_containers.append(container.name)
        return stopped_containers

    def get_containers(self):
        """
        Get all running containers
        :return:
        """
        import docker
        client = docker.from_env()
        return [container for container in client.containers.list(all=True) if
                container.name.startswith(self.config['tag'])]
