import subprocess

from brokerio.app import start, scrub, keys_init, assign
from brokerio.cli.CLI import CLI
import psutil


class BrokerCLI(CLI):
    name = 'broker'
    help = 'Broker Management'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def arg_parser_db(_parser):
        _parser.add_argument('--db_url', help="ArangoDB Connection URL", type=str,
                             default="http://localhost:8529")
        _parser.add_argument('--db_name', help="ArangoDB Database Name", type=str, default="broker")
        _parser.add_argument('--db_user', help="ArangoDB Username", type=str, default="root")
        _parser.add_argument('--db_pass', help="ArangoDB Password", type=str, default="secret")

    @staticmethod
    def arg_parser(_parser):
        _parser.add_argument('--help', help="Show help", action='store_true')

        sub_parser = _parser.add_subparsers(dest='sub_command', help="Commands for managing broker")

        build_parser = sub_parser.add_parser('build', help="Build the broker")
        build_parser.add_argument('--nocache', help="Do not use cache", action='store_true')
        build_parser.add_argument('--network', help="Network name (Default: network_broker)", type=str,
                                  default='network_broker')

        start_parser = sub_parser.add_parser('start', help="Start the broker")
        start_parser.add_argument('--config_file', help="Config file for broker", type=str, default=None)
        BrokerCLI.arg_parser_db(start_parser)
        start_parser.add_argument('--port', help="Port for broker", type=int, default=4852)
        start_parser.add_argument('--redis_url', help="Redis Connection URL", type=str,
                                  default="redis://localhost:6379")
        start_parser.add_argument('--private_key_path', help="Path to private key", type=str, default="./private_key.pem")
        start_parser.add_argument('--workers', help="Number of workers", type=int, default=psutil.cpu_count(logical=True))

        scrub_parser = sub_parser.add_parser('scrub', help="Only run scrub job")
        BrokerCLI.arg_parser_db(scrub_parser)

        init_parser = sub_parser.add_parser('init', help="Init the broker")
        init_parser.add_argument('--private_key_path', help="Path to private key", type=str, default="./private_key.pem")
        BrokerCLI.arg_parser_db(init_parser)

        a_parser = sub_parser.add_parser('assign', help="Assign a role to a user")
        a_parser.add_argument('--role', help="Assign role to user (Default: admin)", type=str, default='admin')
        a_parser.add_argument('--key', help="Public key of user for assigning a role", type=str, default=None)

    def parse(self, args):
        if args.sub_command == 'start':
            start(args)

        elif args.sub_command == 'scrub':
            scrub(args)

        elif args.sub_command == 'init':
            keys_init(args)

        elif args.sub_command == 'assign':
            if args.key is None or args.role is None:
                self.parser.parse_args([args.sub_command, '--help'])
                exit()
            else:
                assign(args)

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

        else:
            print(args)
            self.parser.print_help()
            exit()
