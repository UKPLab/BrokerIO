from brokerio.cli import CLI
from brokerio.guard import start_guard


class GuardCLI(CLI):
    name = 'guard'
    help = 'Start BrokerIO Guard (listen to broadcast messages)'

    def parse(self, args):
        start_guard()
