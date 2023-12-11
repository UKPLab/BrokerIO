from skills.SkillModel import SkillModel
import docker


class Model(SkillModel):
    def __init__(self):
        super().__init__('openai')
        self.help = 'Open AI client'

    def run(self, args):
        """
        Run the skill
        :param args:
        :return:
        """
        # Check if the container is already built
        client = docker.from_env()
        try:
            image = client.images.get(self.tag)
            # Run the container
            container = client.containers.run(
                self.tag,
                detach=True,
                command='python3 -m skills.openai.OASkill',
                environment={
                    'OPENAI_API_KEY': "test"
                }
            )
            print("Running skill {}".format(self.name))
        except docker.errors.ImageNotFound:
            print("Image not found. Please build the container first.")
            exit()

    def set_parser(self, parser):
        super().set_parser(parser)
        self.parser.add_argument('--api_key', help='OpenAI API Key')
        self.parser.add_argument('--model', help='OpenAI Model', default='gpt-35-turbo-0301')

    def build(self, nocache=False):
        """
        Build the docker container
        :param nocache: Do not use cache
        :return:
        """
        # Create a Docker client
        client = docker.from_env()

        try:
            build_logs = client.api.build(
                dockerfile="./models/openai/Dockerfile",
                path="./skills",
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
