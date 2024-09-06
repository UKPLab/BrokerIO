from brokerio.cli import CLI
from brokerio.guard import start_guard


class GuardCLI(CLI):
    name = 'guard'
    help = 'Start BrokerIO Guard (listen to broadcast messages)'

    @staticmethod
    def arg_parser(_parser):
        _parser.add_argument('--help', help="Show help", action='store_true')
        _parser.add_argument('--broker_url', help="Broker URL", type=str, default="http://localhost:4852")

    def parse(self, args):

        if args.help:
            self.parser.print_help()
        else:
            start_guard(args)
