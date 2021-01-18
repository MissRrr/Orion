import argparse
import traceback
import sys
import logdb
import log
import sundry
import consts

from commands import (
    NodeCommands,
    ResourceCommands,
    StoragePoolCommands,
    DiskCommands,
    DiskGroupCommands,
    HostCommands,
    HostGroupCommands,
    MapCommands,
    PortalCommands,
    SyncCommands
)


class MyArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = ('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        return args

    def print_usage(self, file=None):
        logger = log.Log()
        cmd = ' '.join(sys.argv[1:])
        path = sundry.get_path()
        logger.write_to_log('DATA', 'INFO', 'cmd_input', path, {'valid':'1','cmd':cmd})
        logger.write_to_log('INFO', 'INFO', 'finish','', 'print usage')
        if file is None:
            file = sys.stdout
        self._print_message(self.format_usage(), file)

    def print_help(self, file=None):
        logger = log.Log()
        logger.write_to_log('INFO', 'INFO', 'finish','', 'print help')
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help(), file)



class VtelCLI(object):
    """
    Vtel command line client
    """
    def __init__(self):
        consts.init()
        self.logger = log.Log()
        self._node_commands = NodeCommands()
        self._resource_commands = ResourceCommands()
        self._storagepool_commands = StoragePoolCommands()
        self._disk_commands = DiskCommands()
        self._diskgroup_commands = DiskGroupCommands()
        self._host_commands = HostCommands()
        self._hostgroup_commands = HostGroupCommands()
        self._map_commands = MapCommands()
        self._vip_commands = PortalCommands()
        self._sync_commands = SyncCommands()
        self._parser = self.setup_parser()


    def setup_parser(self):
        parser = MyArgumentParser(prog="vtel")
        """
        Set parser vtel sub-parser
        """

        subp = parser.add_subparsers(metavar='',
                                     dest='subargs_vtel')

        parser.add_argument('-v',
                            '--version',
                            dest='version',
                            help='Show current version',
                            action='store_true')

        parser_stor = subp.add_parser(
            'stor',
            help='Management operations for LINSTOR',
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter,
        )


        parser_iscsi = subp.add_parser(
            'iscsi',
            help='Management operations for iSCSI',
            add_help=False)

        # replay function related parameter settings
        parser_replay = subp.add_parser(
            'replay',
            aliases=['re'],
            formatter_class=argparse.RawTextHelpFormatter
        )

        parser_replay.add_argument(
            '-t',
            '--transactionid',
            dest='transactionid',
            metavar='',
            help='transaction id')

        parser_replay.add_argument(
            '-d',
            '--date',
            dest='date',
            metavar='',
            nargs=2,
            help='date')


        self.parser_stor = parser_stor
        self.parser_iscsi = parser_iscsi
        self.parser_replay = parser_replay

        parser_replay.set_defaults(func=self.replay)

        subp_stor = parser_stor.add_subparsers(dest='subargs_stor',metavar='')
        subp_iscsi = parser_iscsi.add_subparsers(dest='subargs_iscsi',metavar='')

        # add all subcommands and argument
        self._node_commands.setup_commands(subp_stor)
        self._resource_commands.setup_commands(subp_stor)
        self._storagepool_commands.setup_commands(subp_stor)

        self._disk_commands.setup_commands(subp_iscsi)
        self._diskgroup_commands.setup_commands(subp_iscsi)
        self._host_commands.setup_commands(subp_iscsi)
        self._hostgroup_commands.setup_commands(subp_iscsi)
        self._map_commands.setup_commands(subp_iscsi)
        self._vip_commands.setup_commands(subp_iscsi)
        self._sync_commands.setup_commands(subp_iscsi)

        parser_iscsi.set_defaults(func=self.print_iscsi_help)
        parser_stor.set_defaults(func=self.print_stor_help)
        parser.set_defaults(func=self.func_vtel)
        return parser


    def func_vtel(self,args):
        if args.version:
            print(f'VersaTEL G2 {consts.VERSION}')
        else:
            self._parser.print_help()

    def print_iscsi_help(self, *args):
        self.parser_iscsi.print_help()

    def print_stor_help(self, *args):
        self.parser_stor.print_help()


    def replay_one(self,dict_input):
        if not dict_input:
            print('There is no command to replay')
            return
        print(f"\n-------------- transaction: {dict_input['tid']}  command: {dict_input['cmd']} --------------")
        consts.set_glo_tsc_id(dict_input['tid'])
        if dict_input['valid'] == '0':
            replay_args = self._parser.parse_args(dict_input['cmd'].split())
            try:
                replay_args.func(replay_args)
            except consts.ReplayExit:
                print('The transaction replay ends')
            except Exception:
                print(str(traceback.format_exc()))
        else:
            print(f"Command error: {dict_input['cmd']} , and cannot be executed")


    def replay_more(self,dict_input):
        print('* MODE : REPLAY *')
        print(f'transaction num : {len(dict_input)}')

        number_list = [str(i) for i in list(range(1,len(dict_input)+1))]
        for i in range(len(dict_input)):
            print(f"{i+1:<3} Transaction ID: {dict_input[i]['tid']:<12} CMD: {dict_input[i]['cmd']}")

        answer = ''
        while answer != 'exit':
            print('Please enter the number to execute replay, or "all", enter "exit" to exit：')
            answer = input()
            if answer in number_list:
                dict_cmd = dict_input[int(answer)-1]
                self.replay_one(dict_cmd)
                consts.set_glo_log_id(0)
            elif answer == 'all':
                for dict_cmd in dict_input:
                    self.replay_one(dict_cmd)
            elif answer != 'exit':
                print('Number error')


    def replay(self,args):
        logger = log.Log()
        logger.log_switch = False
        consts.set_glo_rpl('yes')
        logdb.prepare_db()
        obj_logdb = consts.glo_db()
        if args.transactionid and args.date:
            print('Please specify only one type of data for replay')
            return
        elif args.transactionid:
            dict_cmd = obj_logdb.get_userinput_via_tid(args.transactionid)
            print('* MODE : REPLAY *')
            print(f'transaction num : 1')
            self.replay_one(dict_cmd)
        elif args.date:
            dict_cmd = obj_logdb.get_userinput_via_time(args.date[0],args.date[1])
            self.replay_more(dict_cmd)
        else:
            dict_cmd = obj_logdb.get_all_transaction()
            self.replay_more(dict_cmd)
        return dict_cmd


    def parse(self): # 调用入口
        args = self._parser.parse_args()
        path = sundry.get_path()
        cmd = ' '.join(sys.argv[1:])
        if args.subargs_vtel:
            if args.subargs_vtel not in ['re', 'replay']:
                self.logger.write_to_log('DATA', 'INPUT', 'cmd_input', path, {'valid': '0', 'cmd': cmd})
        else:
            self.logger.write_to_log('DATA','INPUT','cmd_input', path, {'valid':'0','cmd':cmd})
        args.func(args)


def main():
    try:
        cmd = VtelCLI()
        cmd.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nClient exiting (received SIGINT)\n")
    except PermissionError:
        sys.stderr.write("\nPermission denied (log file or other)\n")


if __name__ == '__main__':
    main()