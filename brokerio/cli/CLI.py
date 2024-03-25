class CLI:
    name = 'cli'
    help = "{} Management".format(name)

    def __init__(self, parser):
        self.parser = parser

    @property
    def name(self):
        return type(self).name

    @property
    def help(self):
        return type(self).help

    @staticmethod
    def arg_parser(parser):
        """
        Define additional arguments
        :param parser:
        :return:
        """
        pass

    def parse(self, args):
        """
        Handle the arguments
        :param args: argument object
        :return:
        """
        self.parser.print_help()


def register_client_module(modules, parser, client_class):
    """
    Add a client module to the parser
    :param parser: parser object
    :param client_class: client class
    :return:
    """
    client = client_class()
    parser = parser.add_parser(client.name, help=client.help)
    client.set_parser(parser)
    modules[client.name] = client
