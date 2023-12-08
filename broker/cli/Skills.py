import glob
import subprocess

import docker
import yaml


class Skills:
    def __init__(self):
        self.name = 'skills'
        self.help = "Menu for managing skills"
        self.parser = None
        self.parser_build = None

    def set_parser(self, parser):
        self.parser = parser
        model_parser = parser.add_subparsers(dest='skill_command', help="Commands for managing skills")
        parser_model_list = model_parser.add_parser('list', help="List available skills")
        self.parser_build = model_parser.add_parser('build', help="Build a skill")
        self.parser_build.add_argument('--name', help="Name of the skill to build")

    def handle(self, args):
        if args.skill_command == 'list':
            # search directory for yml files
            yml_files = glob.glob("./skills/*.yml")

            print("Available skills:")

            # load yml files
            for yml_file in yml_files:
                with open(yml_file, "r") as f:
                    config = yaml.load(f, Loader=yaml.FullLoader)
                    if 'name' in config:
                        print("- {} | {}".format(
                            yml_file.replace("./skills/", "").replace(".yml", ""),
                            config['description'] if 'description' in config else 'No description')
                        )
        elif args.skill_command == 'build':
            if args.name is not None:
                self.build(args.name)
            else:
                self.parser_build.print_help()
                exit()
        elif args.skill_command == 'run':

            client = docker.from_env()

            # Define the build context and Dockerfile path
            build_context = './models/llama.cpp'  # Use current directory as the build context
            dockerfile_path = 'Dockerfile'

            # Define volumes
            volumes = {
                './model': {'bind': '/app/model', 'mode': 'rw'},
                './config': {'bind': '/app/config', 'mode': 'rw'}
            }

            # Define the command to be executed inside the container
            command = 'python3 app.py'

            # Define network mode
            network_mode = 'host'

            # Define container options
            container_options = {
                'command': command,
                'network_mode': network_mode,
                'volumes': {k: v for k, v in volumes.items()}
            }

            # Build the Docker image from the subdirectory
            build_output = client.api.build(path=build_context, nocache=True, dockerfile=dockerfile_path,
                                            tag='your_image_tag', decode=True, rm=True)

            # Print build output in real-time
            for chunk in build_output:
                if 'stream' in chunk:
                    for line in chunk['stream'].splitlines():
                        print(line)

            client.containers.run('your_image_tag', detach=True, **container_options)

            exit()

            process = None
            try:
                process = subprocess.Popen(
                    ['docker', 'compose', 'build', '--no-cache', 'transformer'],
                    # Replace 'up' with your desired Docker Compose command
                    cwd="./models/llama.cpp",  # Path to your Docker Compose subdirectory
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )

                for line in process.stdout:
                    # Print live output
                    print(line, end='')

                process.communicate()  # Wait for the process to complete

            except KeyboardInterrupt:
                print("Keyboard interrupt")
            finally:
                if process is not None:
                    try:
                        process.terminate()
                    except OSError:
                        process.kill()

            exit()

            print("TODO: list models")
            client = docker.from_env()
            dockerfile_path = "./models/llama.cpp"

            # Build the Docker image from the subdirectory
            build_output = client.api.build(path=dockerfile_path, tag='your_image_tag', decode=True, rm=True)

            # Print build output in real-time
            for chunk in build_output:
                if 'stream' in chunk:
                    for line in chunk['stream'].splitlines():
                        print(line)


        else:
            self.parser.print_help()
            exit()

    def build(self, model):
        """
        Build a model
        :param model: model name
        :return:
        """
        print("Build model {}".format(model))
        # Load yaml file
        try:
            with open("./models/{}.yml".format(model), "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                print("Config loaded: {}".format(config))
        except FileNotFoundError:
            print("Model {} not found".format(model))
            exit()

        # Build docker image
        client = docker.from_env()

        # Define the build context and Dockerfile path
        build_context = './models/llama.cpp'
        dockerfile_path = 'Dockerfile'

        # Define volumes
        volumes = {
            './model': {'bind': '/app/model', 'mode': 'rw'},
            './config': {'bind': '/app/config', 'mode': 'rw'}
        }

        # Define the command to be executed inside the container
        command = 'python3 app.py'


