

class Models:
    def __init__(self):
        self.name = 'models'
        self.help = "Menu for managing models"
        self.parser = None

    def set_parser(self, parser):
        self.parser = parser
        model_parser = parser.add_subparsers(dest='model_command', help="Commands for managing models")
        parser_model_list = model_parser.add_parser('list', help="List available models")

    def handle(self, args):
        if args.model_command == 'list':
            print("TODO: list models")
        else:
            self.parser.print_help()
            exit()