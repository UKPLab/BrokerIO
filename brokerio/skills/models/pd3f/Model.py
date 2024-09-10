""" Skill for PD3F PDF text extraction

This skill is a simple skill that uses the PD3F PDF text extraction tool to extract text from a PDF file.

https://github.com/pd3f/pd3f

Author: Dennis Zyska
"""

from brokerio.skills.SkillModel import SkillModel


class Model(SkillModel):

    @staticmethod
    def arg_parser(parser):
        """
        Define additional arguments
        :param parser:
        :return:
        """
        pass

    def run(self, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter:
        :return:
        """
        containers = super().run()

        print("Add PD3F containers")
        import docker

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

            print("Connect machine {} to network {}".format(c['name'], c['name']))
            net.connect(c['name'])
            print("Connect machine {} to network {}".format(parsr_name, c['name']))
            net.connect(parsr_name)

        return containers

    def stop(self):
        """
        Stop the skill
        :return:
        """
        container = super().stop()

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
