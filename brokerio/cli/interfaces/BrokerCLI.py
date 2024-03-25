import subprocess

from brokerio.app import start
from brokerio.cli.CLI import CLI


class BrokerCLI(CLI):
    name = 'broker'
    help = 'Broker Management'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def arg_parser(_parser):
        sub_parser = _parser.add_subparsers(dest='sub_command', help="Commands for managing broker")
        build_parser = sub_parser.add_parser('build', help="Build the broker")
        build_parser.add_argument('--nocache', help="Do not use cache", action='store_true')
        build_parser.add_argument('--network', help="Network name (Default: network_broker)", type=str,
                                  default='network_broker')
        start_parser = sub_parser.add_parser('start', help="Start the broker")
        start_parser.add_argument('--env', help="Environment file to load (Default using ENV)", type=str, default="")
        sub_parser = start_parser.add_subparsers(dest='broker_command', help="Commands for broker")
        sub_parser.add_parser('scrub', help="Only run scrub job")
        sub_parser.add_parser('init', help="Init the broker")

        a_parser = sub_parser.add_parser('assign', help="Assign a role to a user")
        a_parser.add_argument('--role', help="Assign role to user (Default: admin)", type=str, default='admin')
        a_parser.add_argument('--key', help="Public key of user for assigning a role", type=str, default=None)

    def parse(self, args):
        if args.sub_command == 'start':
            start(args)

        elif args.sub_command == 'build':
            # running subprocess to build the broker
            process = None
            try:
                process = subprocess.Popen(
                    ['docker', 'compose', '-f', 'docker-compose.yml', '-p', args.network, 'up', '--build', '-d'],
                    # Replace 'up' with your desired Docker Compose command
                    cwd=".",  # Path to your Docker Compose subdirectory
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
        if args.sub_command == 'scrub':
            # TODO: run command locally or in docker container
            pass
        elif args.sub_command == 'init':
            # TODO: run command locally or in docker container
            pass
        elif args.sub_command == 'assign':
            # TODO: run command locally or in docker container
            pass
        else:
            print(args)
            self.parser.print_help()
            exit()
