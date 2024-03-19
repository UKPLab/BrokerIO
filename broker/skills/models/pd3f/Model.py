""" Skill for PD3F PDF text extraction

This skill is a simple skill that uses the PD3F PDF text extraction tool to extract text from a PDF file.

https://github.com/pd3f/pd3f

Author: Dennis Zyska
"""
import docker

from broker.skills.SkillModel import SkillModel


class Model(SkillModel):
    def __init__(self):
        super().__init__('pd3f')
        self.help = 'PD3F PDF text extraction skill'
        self.link = 'https://github.com/pd3f/pd3f'
        self.template = 'simpleSkill'

    def run(self, args, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter:
        :param args:
        :return:
        """
        containers = super().run(args, {
            "environment": {
                'BROKER_URL': args.url,
                'SKILL_NAME': self.name if args.skill == "" else args.skill,
                'TEST': 2
            },
        })

        print("Add PD3F containers")
        client = docker.from_env()

        new_containers = [c for c in containers]
        for c in containers:
            parsr_name = "{}_{}".format(c['name'], 'parsr')
            output = client.containers.run("axarev/parsr:v1.2.2",
                                           name=parsr_name,
                                           restart_policy={"Name": "always"},
                                           detach=True)
            print("Build container {}".format(output.short_id))
            print(output.logs().decode('utf-8'))
            new_containers.append({
                "name": output.name,
                "id": output.short_id
            })

            # link the container to the network
            print("Create network {}".format(c['name']))
            try:
                net = client.networks.get(c['name'])
            except docker.errors.NotFound:
                net = client.networks.create(c['name'], driver="bridge")

            print("Connect machien {} to network {}".format(c['name'], c['name']))
            net.connect(c['name'])
            print("Connect machine {} to network {}".format(parsr_name, c['name']))
            net.connect(parsr_name)

        return containers

    def stop(self, args):
        """
        Stop the skill
        :param args:
        :return:
        """
        container = super().stop(args)

        print("Remove parsr networks")
        client = docker.from_env()
        for c in container:
            try:
                net = client.networks.get(c)
                if net:
                    net.remove()
                    print("Removed network {}".format(c))
            except docker.errors.NotFound:
                pass


    def set_parser(self, parser):
        super().set_parser(parser)

    def build(self, nocache=False):
        """
        Build the docker container
        :param nocache: Do not use cache
        :return:
        """
        super().build(nocache)

        # Create a Docker client
        client = docker.from_env()

        try:
            build_logs = client.api.build(
                dockerfile="Dockerfile",
                path="./broker/skills/models/pd3f",
                tag=self.tag,
                decode=True, rm=True,
                nocache=nocache,
            )
            # Print build output in real-time
            for chunk in build_logs:
                if 'stream' in chunk:
                    for line in chunk['stream'].splitlines():
                        print(line)
        except docker.errors.BuildError as e:
            print("Failed to build Docker image:", e)
