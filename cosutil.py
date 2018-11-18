import os

from gooey import GooeyParser, Gooey
from six.moves.configparser import ConfigParser

from configs import regions


def setup_config(args):
    config_path = os.path.expanduser(args.config_path)

    cp = ConfigParser()

    cp.add_section("common")
    cp.set('common', 'secret_id', args.secret_id)
    cp.set('common', 'secret_key', args.secret_key)
    cp.set('common', 'bucket', args.bucket)
    cp.set('common', 'region', args.region)
    cp.set('common', 'max_thread', str(args.max_thread))
    cp.set('common', 'part_size', str(args.part_size))

    cp.add_section("cosutil")
    if args.no_prefix:
        prefix_type = 'absence'
    elif args.relative_prefix:
        prefix_type = 'relative'
    else:
        prefix_type = 'fixed'
        cp.set('cosutil', 'fixed_prefix', args.fixed_prefix)
    cp.set('cosutil', 'prefix_type', prefix_type)

    cp.write(open(config_path, 'w+'))


def setup_config_parser(subparsers):
    config_parser = subparsers.add_parser(
        'Configuration', help='Configure your AK, SK, region, bucket, etc.')

    file_group = config_parser.add_argument_group("Setting Configuration Into...")
    file_group.add_argument('-c', '--config_path', help="path of config file", type=str,
                            default=os.path.join(os.path.abspath(os.path.curdir), ".cos.conf"))

    config_group = config_parser.add_argument_group("COS Configuration")
    config_group.add_argument('-a', '--secret_id', type=str, required=True, help='secret ID of your account')
    config_group.add_argument('-s', '--secret_key', type=str, required=True, help='secret Key of your account')
    config_group.add_argument('-b', '--bucket', help='bucket ID', type=str, required=True)
    config_group.add_argument('-r', '--region', help='region, e.g. "ap-guangzhou"', type=str, choices=regions,
                              default='ap-guangzhou', required=True)
    config_group.add_argument('-m', '--max_thread', help='the number of threads when uploading (default 5)', type=int,
                              default=5)
    config_group.add_argument('-p', '--part_size', help='the minimal trunk size in MiB when uploading (default 1MiB)',
                              type=int, default=1)

    behavior_group = config_parser.add_argument_group("Upload Behavior")
    behavior_prefix_group = behavior_group.add_mutually_exclusive_group(required=True)
    behavior_prefix_group.add_argument('--no_prefix', action='store_true',
                                       help='don\'t append any path prefix with when uploading')
    behavior_prefix_group.add_argument('--relative_prefix', action='store_true',
                                       help='append path prefix with path relative to working directory when uploading')
    # TODO: without value it fails
    behavior_prefix_group.add_argument(
        '--fixed_prefix', help='append fixed path prefix when uploading', type=str, default="/",
        gooey_options={
            'validator': {
                'test': 'user_input.endswith("/")',
                'message': 'Path prefix should be end with "/"'
            }
        }
    )

    config_parser.set_defaults(func=setup_config)


@Gooey(program_name='COS Utils', navigation='TABBED')
def main():
    parser = GooeyParser(description='Yet another friendly COS utilities')
    subparsers = parser.add_subparsers(help='commands')

    setup_config_parser(subparsers)

    upload_parser = subparsers.add_parser('Upload', help='Upload file to COS')

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
