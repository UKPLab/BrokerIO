

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
