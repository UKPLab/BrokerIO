from skills.SkillModel import SkillModel
import docker


class Model(SkillModel):
    def __init__(self):
        super().__init__('openai')
        self.help = 'Open AI client'
        self.template = 'simpleSkill'

    def run(self, args):
        """
        Run the skill
        :param args:
        :return:
        """
        # Check if the container is already built
        client = docker.from_env()
        try:
            print("Running skill {}".format(self.name))

            image = client.images.get(self.tag)
            print("Found image {}".format(image.short_id))
            # Run the container
            container = client.containers.run(
                self.tag,
                detach=True,
                command='python3 /app/connect.py',
                environment={
                    'OPENAI_API_KEY': "test",
                    'BROKER_URL': args.url,

                },
                network="nlp_api_main_default"
            )
            print("Build container {}".format(container.short_id))

            # Print the container logs
            print(container.logs().decode('utf-8'))

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
        super().build(nocache)

        # Create a Docker client
        client = docker.from_env()

        try:
            build_logs = client.api.build(
                dockerfile="Dockerfile",
                path="./skills/models/openai",
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
