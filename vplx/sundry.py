# coding:utf-8
import time
import os
import traceback
import re
import prettytable
import sys
import pprint
import subprocess
from functools import wraps
import colorama as ca

import consts
import log



def deco_record_exception(func):
    """
    Decorator
    Get exception, throw the exception after recording
    :param func:Command binding function
    """
    def wrapper(self,*args):
        try:
            return func(self,*args)
        except Exception as e:
            self.logger.write_to_log('DATA','DEBUG','exception','', str(traceback.format_exc()))
            raise e
    return wrapper


def deco_comfirm_del(type):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        def wrapper(self,*args):
            cli_args = args[0]
            if cli_args.yes:
                func(self,*args)
            else:
                print(f"Are you sure you want to delete this {type}? If yes, enter 'y/yes'")
                answer = get_answer()
                # answer = 'y'
                if answer in ['y', 'yes']:
                    func(self,*args)
                else:
                    prt_log('Delete canceled',0)
        return wrapper
    return decorate


def get_answer():
    logger = log.Log()
    rpl = consts.glo_rpl()
    logdb = consts.glo_db()
    transaction_id = consts.glo_tsc_id()

    if rpl == 'no':
        answer = input()
        # answer = 'y'
        logger.write_to_log('DATA', 'INPUT', 'confirm_input', 'confirm deletion', answer)
    else:
        time,answer = logdb.get_anwser(transaction_id)
        if not time:
            time = ''
        print(f'RE:{time:<20} <input> user input: {answer}\n')
    return answer



# Get the path of the program
def get_path():
    return os.getcwd()


def re_findall(re_string, tgt_string):
    logger = log.Log()
    re_ = re.compile(re_string)
    oprt_id = log.create_oprt_id()
    logger.write_to_log('OPRT', 'REGULAR', 'findall', oprt_id, {'re': re_, 'string': tgt_string})
    re_result = re_.findall(tgt_string)
    logger.write_to_log('DATA', 'REGULAR', 'findall', oprt_id, re_result)
    return re_result


def re_search(re_string, tgt_stirng,output_type='group'):
    logger = log.Log()
    re_ = re.compile(re_string)
    oprt_id = log.create_oprt_id()
    logger.write_to_log('OPRT','REGULAR','search',oprt_id, {'re':re_,'string':tgt_stirng})
    re_result = re_.search(tgt_stirng)
    if re_result:
        if output_type == 'group':
            re_result = re_result.group()
        else:
            re_result = re_result.groups()
    logger.write_to_log('DATA', 'REGULAR', 'search', oprt_id, re_result)
    return re_result


# def show_iscsi_data(list_header, dict_data):
#     table = prettytable.PrettyTable()
#     table.field_names = list_header
#     if dict_data:
#         for i,j in dict_data.items():
#             data_one = [i,(' '.join(j) if isinstance(j,list) == True else j)]
#             table.add_row(data_one)
#     else:
#         pass
#     return table


# def show_spe_map_data(list_header, list_data):
#     table = prettytable.PrettyTable()
#     table.field_names = list_header
#     if list_data:
#         for i in list_data:
#             table.add_row(i)
#     else:
#         pass
#     return table


# def show_map_data(list_header, dict_data):
#     table = prettytable.PrettyTable()
#     table.field_names = list_header
#     if dict_data:
#         # {map1:{"HostGroup":[hg1,hg2],"DiskGroup":[dg1,dg2]} => [map1,"hg1 hg2","dg1 dg2"]}
#         for i, j in dict_data.items():
#             data_list = [i,
#                          (' '.join(j["HostGroup"]) if isinstance(j["HostGroup"], list) == True else j["HostGroup"]),
#                          (' '.join(j["DiskGroup"]) if isinstance(j["DiskGroup"], list) == True else j["DiskGroup"])]
#             table.add_row(data_list)
#     return table


def make_table(list_header,list_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if list_data:
        for i in list_data:
            table.add_row(i)
    return table


def change_pointer(new_id):
    consts.set_glo_log_id(new_id)

def deco_cmd(type):
    """
    装饰器
    用于装饰系统命令的执行
    :param type: 系统命令的类型(sys,linstor,crm)
    :return:返回命令执行结果
    """

    def decorate(func):
        @wraps(func)
        def wrapper(cmd):
            RPL = consts.glo_rpl()
            oprt_id = log.create_oprt_id()
            func_name = traceback.extract_stack()[-2][2]  # 装饰器获取被调用函数的函数名
            if RPL == 'no':
                logger = log.Log()
                logger.write_to_log('DATA', 'STR', func_name, '', oprt_id)
                logger.write_to_log('OPRT', 'CMD', type, oprt_id, cmd)
                result_cmd = func(cmd)
                logger.write_to_log('DATA', 'CMD', type, oprt_id, result_cmd)
                return result_cmd
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func_name)
                if id_result['oprt_id']:
                    cmd_result = logdb.get_oprt_result(id_result['oprt_id'])
                else:
                    cmd_result = {'time':'','result':''}
                if type != 'sys' and cmd_result['result']:
                    result = eval(cmd_result['result'])
                    result_output = result['rst']
                else:
                    result = cmd_result['result']
                    result_output = cmd_result['result']
                print(f"RE:{id_result['time']:<20} <command>cmd：\n{cmd}")
                print(f"RE:{cmd_result['time']:<20} <command>result：\n{result_output}")
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])

            return result
        return wrapper
    return decorate


@deco_cmd('sys')
def execute_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    output = p.stdout.read().decode()
    return output




def prt(str_, warning_level=0):
    if isinstance(warning_level, int):
        warning_str = '*' * warning_level
    else:
        warning_str = ''
    rpl = consts.glo_rpl()

    if rpl == 'no':
        print(str(str_))
    else:
        db = consts.glo_db()
        data = db.get_cmd_output(consts.glo_tsc_id())
        if not data["time"]:
            data["time"] = ''
        print(f'RE:{data["time"]:<20} <output>log output：{warning_str:<4}\n{data["output"]}')
        print(f'RE:{"":<20} <output>this time output：{warning_str:<4}\n{str_}\n')
        change_pointer(int(data["db_id"]))

def prt_log(str_, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    logger = log.Log()
    RPL = consts.glo_rpl()
    if RPL == 'yes':
        prt(str_, warning_level)
    elif RPL == 'no':
        prt(str_, warning_level)

    if warning_level == 0:
        logger.write_to_log('INFO', 'INFO', 'finish', 'output', str_)
    elif warning_level == 1:
        logger.write_to_log('INFO', 'WARNING', 'fail', 'output', str_)
    elif warning_level == 2:
        logger.write_to_log('INFO', 'ERROR', 'exit', 'output', str_)
        if RPL == 'no':
            sys.exit()
        else:
            raise consts.ReplayExit


def deco_color(func):
    """
    装饰器，给特定的linstor数据进行着色
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args):
        status_true = ['UpToDate', 'Online', 'Ok', 'InUse']
        data = func(*args)
        for lst in data:
            if lst[-1] in status_true:
                lst[-1] = ca.Fore.GREEN + lst[-1] + ca.Style.RESET_ALL
            else:
                lst[-1] = ca.Fore.RED + lst[-1] + ca.Style.RESET_ALL
        return data
    return wrapper




def deco_json_operation(str):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            # print(traceback.extract_stack()[-2])
            # print(traceback.extract_stack()[-3])
            if RPL == 'no':
                logger = log.Log()
                oprt_id = log.create_oprt_id()
                logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
                logger.write_to_log('OPRT', 'JSON', func.__name__, oprt_id, args)
                result = func(self,*args)
                logger.write_to_log('DATA', 'JSON', func.__name__, oprt_id,result)
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
                json_result = logdb.get_oprt_result(id_result['oprt_id'])
                if json_result['result']:
                    result = eval(json_result['result'])
                else:
                    result = ''
                print(f"RE:{id_result['time']} {str}:")
                pprint.pprint(result)
                print()
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate


def deco_db_insert(func):
    @wraps(func)
    def wrapper(self, sql, data, tablename):
        RPL = consts.glo_rpl()
        if RPL == 'no':
            logger = log.Log()
            oprt_id = log.create_oprt_id()
            logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
            logger.write_to_log('OPRT', 'SQL', func.__name__, oprt_id, sql)
            func(self,sql, data, tablename)
            logger.write_to_log('DATA', 'SQL', func.__name__, oprt_id, data)
        else:
            logdb = consts.glo_db()
            id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
            func(self, sql, data, tablename)
            print(f"RE:{id_result['time']} <sql>insert table: {tablename}")
            print(f"RE:{id_result['time']} <sql>insert data:")
            for i in data:
                print(i)
            print()# 格式上的换行
            if id_result['db_id']:
                change_pointer(id_result['db_id'])
    return wrapper


def handle_exception():
    rpl = consts.glo_rpl()
    if rpl == 'yes':
        print('The Data cannot be obtained in the log, and the program cannot continue to execute normally')
        raise consts.ReplayExit
    else:
        print('The command result cannot be obtained, please check')
        raise consts.CmdError


