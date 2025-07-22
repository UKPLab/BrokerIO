import importlib.util
import os
import pkgutil
import pathlib

import brokerio.skills.models
from brokerio.cli import CLI, Colors
from brokerio.skills import load_config


def load_skills(path):
    """
    Load all available skills
    :return:
    """
    skills = {}
    for importer, modname, ispkg in pkgutil.iter_modules(path, prefix=''):
        if ispkg:
            # get module
            module_path = os.path.join(importer.path, modname)
            spec = importlib.util.spec_from_file_location(modname, module_path + "/Model.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            model_class = getattr(module, 'Model')

            skills[modname] = {
                "importer": importer,
                "modname": modname,
                "module": model_class,
                "config": load_config(os.path.join(importer.path, modname))
            }
    return skills


def list_skills(args):
    """
    List all skills
    :return:
    """
    print(Colors.HEADER + "BrokerIO basic skills:" + Colors.ENDC)
    print(Colors.BOLD + " {:<25s} {:<10s}".format("Name", "Description") + Colors.ENDC)
    basic_skills = load_skills(brokerio.skills.models.__path__)
    for skill in basic_skills:
        print(" {:<25s} {:<10s}".format(basic_skills[skill]['config']['name'], basic_skills[skill]['config']['desc']))
    if args.skill_dir != "":
        additional_skills = load_skills([args.skill_dir])
        print(Colors.HEADER + "Additional skills from path {}:".format(args.skill_dir) + Colors.ENDC)
        print(Colors.BOLD + " {:<25s} {:<10s}".format("Name", "Description") + Colors.ENDC)
        for skill in additional_skills:
            print(" {:<25s} {:<10s}".format(additional_skills[skill]['config']['name'],
                                            additional_skills[skill]['config']['desc']))


class SkillsCLI(CLI):
    name = 'skills'
    help = "Menu for managing skills"

    @staticmethod
    def arg_parser(_parser):

        _parser.add_argument('--skill_dir', help="Define the directory where the skills are located", type=str,
                             default=brokerio.skills.models.__path__[0])
        _parser.add_argument('--help', help="Show help", action='store_true')

        skill_dir = _parser.parse_known_args()[0].skill_dir

        model_parser = _parser.add_subparsers(dest='skill_command', help="Commands for managing skills")
        parser_model_list = model_parser.add_parser('list', help="List available skills")

        skills = load_skills([skill_dir])
        if len(skills) == 0:
            print(Colors.FAIL + "No skills found in path {} ... end without building...".format(skill_dir) + Colors.ENDC)
            exit()

        parser_build = model_parser.add_parser('build', help="Build a skill")
        subparser = parser_build.add_subparsers(dest='skill_name', help="Skill name to build")
        for skill in skills:
            skill_parser = subparser.add_parser(skills[skill]['modname'], help=skills[skill]['config']['desc'])
            skill_parser.add_argument('--nocache', help='Do not use cache', action='store_true')

        parser_run = model_parser.add_parser('run', help="Run a skill")
        subparser = parser_run.add_subparsers(dest='skill_name', help="Skill name to run")
        for skill in skills:
            skill_parser = subparser.add_parser(skills[skill]['modname'], help=skills[skill]['config']['desc'])
            skill_parser.add_argument('--url', help='URL of the broker', default=os.environ.get('BROKER_URL'))
            skill_parser.add_argument('--num_containers', help='Number of containers to start (default: 1)', type=int,
                                      default=1)
            skill_parser.add_argument('--container_suffix',
                                      help="Add a suffix to container name to start different containers (Default = '')",
                                      default='')
            skill_parser.add_argument('--network', help='Network name (Default: network_broker)', type=str,
                                      default='network_broker')
            skill_parser.add_argument('--skill', help='Name of the skill', default='')
            skills[skill]['module'].arg_parser(skill_parser)

        parser_stop = model_parser.add_parser('stop', help="Stop a skill")
        subparser = parser_stop.add_subparsers(dest='skill_name', help="Skill name to stop")
        for skill in skills:
            skill_parser = subparser.add_parser(skills[skill]['modname'], help=skills[skill]['config']['desc'])
            skill_parser.add_argument('--timeout', help='Timeout for stopping the container (Default: 10)', default=10,
                                      type=int)
            skill_parser.add_argument('--only_stop', help='Only stop the container, do not remove it',
                                      action='store_true')
            skill_parser.add_argument('--container_suffix',
                                      help="Add a suffix to container name to start different containers (Default = '')",
                                      default='')

    def parse(self, args):

        skills = load_skills([args.skill_dir])

        if args.skill_command == 'build':
            if args.skill_name is None or args.skill_name not in skills:
                self.parser.parse_args([args.skill_command, '--help'])
            else:
                skill = skills[args.skill_name]
                print(Colors.BOLD + "Start building process for skill {}...".format(
                    skill['config']['name']) + Colors.ENDC)
                print(skill)
                skill['module'](self.parser, args).build()
        elif args.skill_command == 'list':
            list_skills(args)
        elif args.skill_command == 'run':
            if args.skill_name is None or args.skill_name not in skills:
                self.parser.parse_args([args.skill_command, '--help'])
            else:
                skill = skills[args.skill_name]
                print(Colors.BOLD + "Start run process for skill {}...".format(
                    skill['config']['name']) + Colors.ENDC)
                skill['module'](self.parser, args).run()
        elif args.skill_command == 'stop':
            if args.skill_name is None or args.skill_name not in skills:
                self.parser.parse_args([args.skill_command, '--help'])
            else:
                skill = skills[args.skill_name]
                print(Colors.BOLD + "Stop containers for skill {}...".format(
                    skill['config']['name']) + Colors.ENDC)
                skill['module'](self.parser, args).stop()
        else:
            self.parser.print_help()
            return
