# import os
# import sys
import time
from unittest.mock import patch

import pytest

# import iscsi_json
import iscsi_json
from execute import iscsi
import subprocess
from execute.crm import execute_crm_cmd


class TestDisk:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py stor r c res_test2 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        self.disk = iscsi.Disk()


    def teardown_class(self):
        subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test2 -y', shell=True)
        subprocess.run('python3 vtel.py stor r s', shell=True)
        # json 文件不能及时更新,调用方法进行手动更新该对象（不调用的话 json 文件的disk 还是在）
        print('teardown')
        self.disk.show('all')

    # 根据 linstor 资源更新 disk，无传入参数，返回 disks 字典(可能为空)
    def test_update_disk(self):
        """该方法根据 linstor 资源更新 disk，测试用例包括获取非空字典/空字典"""
        length = len(self.disk.update_disk())
        assert len(self.disk.update_disk()) >= 2
        # 清空 disk
        subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test2 -y', shell=True)
        subprocess.run('python3 vtel.py stor r s', shell=True)
        assert len(self.disk.update_disk()) == length-2

    def test_show(self):
        """展示disk"""
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py stor r c res_test2 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        assert len(self.disk.show('all')) >= 2
        assert self.disk.show('res_test1')[0][0] == 'res_test1'
        # 不存在
        assert self.disk.show('res_test3') == []

    # Disk 类变动下列方法已修改为 show
    # # 获取 linstor res
    # def test_get_all_disk(self):
    #     assert 'res_test1' in self.disk.get_all_disk()
    #     assert 'res_test2' in self.disk.get_all_disk()
    #
    # # 这个函数应该明确获得指定disk,如果没有获得指定disk则return None
    # def test_get_spe_disk(self):
    #     assert self.disk.get_spe_disk('res_test1')
    #     assert self.disk.get_spe_disk('res_test') is None
    #
    # # 该函数没有返回值，调用了本模块get_all_disk()和sundry的show_iscsi_data()
    # def test_show_all_disk(self):
    #     assert self.disk.show_all_disk() is None
    #
    # # 该函数没有返回值，调用了本模块get_spe_disk()和sundry的show_iscsi_data()
    # def test_show_spe_disk(self):
    #     assert self.disk.show_spe_disk('res_test') is None


class TestHost:

    def setup_class(self):
        # subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest0001', shell=True)
        # subprocess.run('python3 vtel.py iscsi h c test_host_hg iqn.2020-04.feixitek.com:pytest0991', shell=True)
        # subprocess.run('python3 vtel.py iscsi h s', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg c test_hg test_host_hg', shell=True)
        # subprocess.run('python3 vtel.py iscsi h s', shell=True)
        self.host = iscsi.Host()
        self.hostg = iscsi.HostGroup()
        self.host.create('test_host', 'iqn.2020-04.feixitek.com:pytest001')
        self.host.create('test_host_hg', 'iqn.2020-04.feixitek.com:pytest0991')
        self.host.show('all')
        self.hostg.create('test_hg', ['test_host_hg'])

    def teardown_class(self):
        # subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host_hg -y', shell=True)
        self.hostg.delete('test_hg')
        self.host.delete('test_host')
        self.host.delete('test_host_hg')
        self.host.show('all')

    # # 已存在返回 None ，新建成功返回 True
    # def test_create_host(self):
    #     # 存在
    #     with patch('builtins.print') as terminal_print:
    #         self.host.create_host('test_host', 'iqn.2020-04.feixitek.com:pytest001')
    #         terminal_print.assert_called_with('Fail! The Host test_host already existed.')
    #     # 不存在，但iqn 格式不正确（要未新建过的host名才会判断iqn格式）
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.host.create_host('test_host3', 'iqn1')
    #             terminal_print.assert_called_with('The format of IQN is wrong. Please confirm and fill in again.')
    #     assert exsinfo.type == SystemExit
    #     # 新建成功
    #     assert self.host.create_host('test_host1', 'iqn.2020-04.feixitek.com:pytest01')
    #
    # # 已存在返回该host ，不存在返回None
    # def test_get_spe_host(self):
    #     assert self.host.get_spe_host('test_host')
    #     assert not self.host.get_spe_host('test_host2')
    #
    # # 该函数没有返回值，调用了本模块get_all_host()和sundry的show_iscsi_data()
    # def test_show_all_host(self):
    #     # 等价于 assert not None
    #     assert not self.host.show_all_host()
    #     # self.hostgroup.create_hostgroup('test_dg', ['test_host_dg'])
    #     # self.hostgroup.show_all_hostgroup()
    #
    # # 该函数没有返回值，调用了本模块get_spe_host()和sundry的show_iscsi_data()
    # def test_show_spe_host(self):
    #     # 等价于 assert not None
    #     assert not self.host.show_spe_host('test_host_hg')
    #
    # def test_modify_host(self):
    #     # 不存在 host
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.host.modify_host('test_hostABC', 'iqn.2020-04.feixitek.com:pytest0999')
    #             terminal_print.assert_called_with('不存在这个host可以去进行修改')
    #     assert exsinfo.type == SystemExit
    #     #
    #
    # # 1.先检查host 是否存在，不存在输出提示语句 2.再判断该host 是否已经配置在HostGroup里，已配置返回输出提示语句
    # # 3.不满足前两个返回条件，删除后返回True
    # def test_delete_host(self):
    #     # 不存在
    #     print('delete_host test_funtion')
    #     with patch('builtins.print') as terminal_print:
    #         self.host.delete_host('test_hostABC')
    #         terminal_print.assert_called_with('Fail! Can\'t find test_hostABC')
    #     # 删除已存在而且没有配置在HostGroup中的host
    #     assert self.host.delete_host('test_host1')
    #     # 已配置用例有待添加
    #     with patch('builtins.print') as terminal_print:
    #         self.host.delete_host('test_host_hg')
    #         terminal_print.assert_called_with('Fail! The host in ... hostgroup.Please delete the hostgroup first')
    #     # self.hostgroup.delete_hostgroup('hg1')
    #
    # # 返回所有host，如果host为空，返回{},否则返回host字典
    # def test_get_all_host(self):
    #     self.hostgroup = iscsi.HostGroup()
    #     #
    #     # self.host.delete_host('test_host_hg')
    #     # host 不为空
    #     assert self.host.get_all_host()
    #     # host 为空
    #     print('delete diskgroup：')
    #     self.hostgroup.delete_hostgroup('test_hg')
    #     print('first delete host：')
    #     self.host.delete_host('test_host')
    #     print('seconde delete host：')
    #     self.host.delete_host('test_host_hg')
    #     self.host.show_all_host()
    #     self.host.get_spe_host('test_host_hg')
    #     assert self.host.get_all_host() == {}

    # -------------  add -------------- 2020.12.28
    def test_check_iqn(self):
        # ----- modify ------ 2021.01.11
        assert self.host._check_iqn('iqn1') is False
        assert self.host._check_iqn('iqn.2020-04.feixitek.com:pytest01') is True

    # ------------- modify ------------ 2021.01.11

    # 已存在返回 None ，iqn 格式不对返回 None ，新建成功返回 True
    def test_create(self):
        """创建host，测试用例包括 host 已存在/iqn格式不正确/创建成功"""
        # 已存在
        with patch('builtins.print') as terminal_print:
            self.host.create('test_host', 'iqn.2020-04.feixitek.com:pytest001')
            terminal_print.assert_called_with('Fail! The Host test_host already existed.')
        # 不存在，但iqn 格式不正确（要未新建过的host名才会判断iqn格式）
        with patch('builtins.print') as terminal_print:
            self.host.create('test_host3', 'iqn1')
            terminal_print.assert_called_with('The format of IQN is wrong. Please confirm and fill in again.')
        # 新建成功
        assert self.host.create('test_host1', 'iqn.2020-04.feixitek.com:pytest01')

    def test_show(self):
        """展示host，测试用例包括：全部 host 展示/展示指定 host /指定 host 不存在"""
        assert len(self.host.show('all')) >= 1
        assert self.host.show('test_host1') == [['test_host1', 'iqn.2020-04.feixitek.com:pytest01']]
        # 不存在
        assert self.host.show('test_host3') == []

    # 修改失败：1.不存在，return None 输入提示语句；修改成功：
    def test_modify(self):
        """修改host，测试用例包括 host 不存在/修改成功"""
        # 不存在 host
        with patch('builtins.print') as terminal_print:
            self.host.modify('test_hostABC', 'iqn.2020-04.feixitek.com:pytest0999')
            terminal_print.assert_called_with('Fail! Can\'t find test_hostABC')
        # 修改成功
        assert not self.host.modify('test_host1', 'iqn.2020-04.feixitek.com:pytest0999')

    # 删除失败：1.不存在，return None 输入提示语句 2.已配置在 HostGroup，return None 输出提示语句；删除成功： return True
    def test_delete(self):
        """删除 host，测试用例包括 host 不存在/ host 已配置在 HostGroup 中/删除成功"""
        # 不存在
        print('delete_host test_funtion')
        with patch('builtins.print') as terminal_print:
            self.host.delete('test_hostABC')
            terminal_print.assert_called_with('Fail! Can\'t find test_hostABC')
        # 删除已存在而且没有配置在HostGroup中的host
        assert self.host.delete('test_host1')
        # 已配置 HostGroup
        with patch('builtins.print') as terminal_print:
            self.host.delete('test_host_hg')
            terminal_print.assert_called_with('Fail! The host in ... hostgroup.Please delete the hostgroup first')


class TestDiskGroup:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest0999', shell=True)
        # subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg c test_hg test_host', shell=True)
        # 创建 Map
        # subprocess.run('python3 vtel.py iscsi m c map1 -dg test_dg -hg test_hg', shell=True)
        # subprocess.run('python3 vtel.py iscsi m s', shell=True)
        self.host = iscsi.Host()
        self.hostg = iscsi.HostGroup()
        self.diskg = iscsi.DiskGroup()
        self.map = iscsi.Map()
        self.host.create('test_host', 'iqn.2020-04.feixitek.com:pytest0999')
        self.diskg.create('test_dg', ['res_test'])
        self.hostg.create('test_hg', ['test_host'])
        self.map.create('map1', ['test_hg'], ['test_dg'])

    def teardown_class(self):
        print('teardown')
        try:
            execute_crm_cmd('crm res stop res_test')
            execute_crm_cmd('crm conf del res_test')
            execute_crm_cmd('crm res stop res_test1')
            execute_crm_cmd('crm conf del res_test1')
        except Exception:
            print(Exception)
        finally:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)

        self.hostg.delete('test_hg')
        self.host.delete('test_host')
        subprocess.run('python3 vtel.py iscsi d s', shell=True)

    # # 1.判断 DiskGroup 是否存在，存在返回 None 2.遍历 disk 列表，若发现 disk 不存在返回 None 3.创建成功返回 True
    # def test_create_diskgroup(self):
    #     # DiskGroup 已存在
    #     assert not self.diskg.create_diskgroup('test_dg', ['res_test'])
    #     with patch('builtins.print') as terminal_print:
    #         self.diskg.create_diskgroup('test_dg', ['res_test'])
    #         terminal_print.assert_called_with('Fail! The Disk Group test_dg already existed.')
    #     # disk 不存在
    #     with patch('builtins.print') as terminal_print:
    #         self.diskg.create_diskgroup('test_dg1', ['res_test', 'res_test0'])
    #         terminal_print.assert_called_with('Fail! Can\'t find res_test0.Please give the true name.')
    #     # 创建成功的测试用例
    #     assert self.diskg.create_diskgroup('test_dg1', ['res_test'])
    #
    # # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    # def test_get_spe_diskgroup(self):
    #     # DiskGroup 不存在测试用例
    #     assert not self.diskg.get_spe_diskgroup('test_dg2')
    #     # DiskGroup 存在测试用例
    #     assert self.diskg.get_spe_diskgroup('test_dg1')
    #
    # # 该函数没有返回值，调用了本模块get_all_diskgroup()和sundry的show_iscsi_data()
    # def test_show_all_diskgroup(self):
    #     assert self.diskg.show_all_diskgroup() is None
    #
    # # 该函数没有返回值，调用了本模块get_spe_diskgroup()和sundry的show_iscsi_data()
    # def test_show_spe_diskgroup(self):
    #     assert self.diskg.show_spe_diskgroup('test_dg1') is None
    #
    # # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # # 这个方法无返回值
    # def test_delete_diskgroup(self):
    #     with patch('builtins.print') as terminal_print:
    #         self.diskg.delete_diskgroup('test_dg2')
    #         terminal_print.assert_called_with('Fail! Can\'t find test_dg2')
    #     # 保留测试用例，该分支有bug
    #     with patch('builtins.print') as terminal_print:
    #         self.map.show_spe_map('map1')
    #         self.diskg.delete_diskgroup('test_dg')
    #         terminal_print.assert_called_with('Fail! The diskgroup already map,Please delete the map')
    #     with patch('builtins.print') as terminal_print:
    #         self.diskg.delete_diskgroup('test_dg1')
    #         terminal_print.assert_called_with('Delete success!')

    # -------------- modify -------------- 2021.01.11
    def test_create(self):
        """创建 diskgroup，测试用例包括：diskgroup已存在，创建失败/所配置的disk不存在，创建失败/创建成功"""
        # DiskGroup 已存在
        assert not self.diskg.create('test_dg', ['res_test'])
        with patch('builtins.print') as terminal_print:
            self.diskg.create('test_dg', ['res_test'])
            terminal_print.assert_called_with('Fail! The Disk Group test_dg already existed.')
        # disk 不存在
        with patch('builtins.print') as terminal_print:
            self.diskg.create('test_dg1', ['res_test', 'res_test0'])
            terminal_print.assert_called_with('Fail! Can\'t find res_test0.Please give the true name.')
        # 创建成功的测试用例
        assert self.diskg.create('test_dg1', ['res_test'])

    def test_show(self):
        """展示 diskgroup"""
        assert self.diskg.show('all') == [['test_dg', 'res_test'], ['test_dg1', 'res_test']]
        assert self.diskg.show('test_dg1') == [['test_dg1', 'res_test']]
        assert self.diskg.show('test_dg0') == []

    def test_delete(self):
        """删除 diskgroup，测试用例包括：diskg不存在，删除失败/已配置在map中，删除失败/删除成功"""
        with patch('builtins.print') as terminal_print:
            self.diskg.delete('test_dg2')
            terminal_print.assert_called_with('Fail! Can\'t find test_dg2')
        # 保留测试用例，该分支有bug
        with patch('builtins.print') as terminal_print:
            # self.map.show('map1')
            self.diskg.delete('test_dg')
            terminal_print.assert_called_with('Fail! The diskgroup already map,Please delete the map')
        with patch('builtins.print') as terminal_print:
            self.diskg.delete('test_dg1')
            terminal_print.assert_called_with('Delete success!')

    # -----------   add  -----------------  2020.12.28
    def test_add_disk(self):
        """diskgroup 新增 disk"""
        # 新增成功
        assert not self.diskg.add_disk('test_dg', ['res_test1'])
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.diskg.add_disk('test_dg2', ['res_test1'])
            terminal_print.assert_called_with('Fail！Can\'t find test_dg2')
        with patch('builtins.print') as terminal_print:
            self.diskg.add_disk('test_dg', ['res_test'])
            terminal_print.assert_called_with('res_test已存在test_dg中')
        with patch('builtins.print') as terminal_print:
            self.diskg.add_disk('test_dg', ['res_O'])
            terminal_print.assert_called_with('json文件中不存在res_O，无法进行添加')

    def test_remove_disk(self):
        """diskgroup 移除 disk"""
        print(self.diskg.show('test_dg'))
        assert not self.diskg.remove_disk('test_dg', ['res_test'])
        # 移除失败
        with patch('builtins.print') as terminal_print:
            self.diskg.remove_disk('test_dg2', ['res_test1'])
            terminal_print.assert_called_with('Fail！Can\'t find test_dg2')
        with patch('builtins.print') as terminal_print:
            self.diskg.remove_disk('test_dg', ['res_O'])
            terminal_print.assert_called_with('test_dg中不存在成员res_O，无法进行移除')
        # 只有一个资源移除后是否会删掉该dg , 会移除该 hg 和 所配置该 hg 的map
        with patch('builtins.print') as terminal_print:
            self.diskg.remove_disk('test_dg', ['res_test1'])
            terminal_print.assert_called_with('相关的map已经修改/删除')
        # self.map.delete_map('map1')
        # self.diskg.delete_diskgroup('test_dg')

    # # 返回所有 DiskGroup，如果为 DiskGroup 空，返回{},否则返回 DiskGroup 非空字典
    # def test_get_all_diskgroup(self):
    #     # DiskGroup 不为空
    #     assert self.diskg.create_diskgroup('test_dg1', ['res_test'])
    #     print('show all diskgroup')
    #     self.diskg.show_all_diskgroup()
    #     assert self.diskg.get_all_diskgroup()
    #     # DiskGroup 为空
    #     # self.map.delete_map('map1')
    #     self.diskg.delete_diskgroup('test_dg1')
    #     assert self.diskg.get_all_diskgroup() == {}


class TestHostGroup:

    def setup_class(self):
        # 请注意对象实例化与命令运行顺序
        # subprocess.run('python3 vtel.py iscsi h c test_host1 iqn.2020-04.feixitek.com:pytest01', shell=True)
        # subprocess.run('python3 vtel.py iscsi h c test_host2 iqn.2020-04.feixitek.com:pytest002', shell=True)
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg c test_hg test_host1', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg s', shell=True)
        # 创建 Map
        # subprocess.run('python3 vtel.py iscsi m c map1 -dg test_dg -hg test_hg', shell=True)
        # subprocess.run('python3 vtel.py iscsi m s', shell=True)
        self.host = iscsi.Host()
        self.hostg = iscsi.HostGroup()
        self.map = iscsi.Map()
        self.diskg = iscsi.DiskGroup()
        self.host.create('test_host1', 'iqn.2020-04.feixitek.com:pytest01')
        self.host.create('test_host2', 'iqn.2020-04.feixitek.com:pytest002')
        self.diskg.create('test_dg', ['res_test'])
        self.hostg.create('test_hg', ['test_host1'])
        self.map.create('map1', ['test_hg'], ['test_dg'])

    def teardown_class(self):
        # subprocess.run('python3 vtel.py iscsi m d map1 -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg d test_dg -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host1 -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host2 -y', shell=True)
        # self.map.delete_map('map1')
        self.diskg.delete('test_dg')
        self.hostg.delete('test_hg')
        self.host.delete('test_host1')
        self.host.delete('test_host2')
        execute_crm_cmd('crm res stop res_test')
        execute_crm_cmd('crm conf del res_test')
        subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)

    # # 1.判断 HostGroup 是否存在，存在返回 None 2.遍历 Host 列表，若发现 Host 不存在返回 None 3.创建成功返回 True
    # def test_create_hostgroup(self):
    #     # 已存在 HostGroup 测试用例
    #     with patch('builtins.print') as terminal_print:
    #         self.hostg.create_hostgroup('test_hg', ['test_host1'])
    #         terminal_print.assert_called_with('Fail! The HostGroup test_hg already existed.')
    #     # 提供的 host 列表中有不存在的 host 测试用例
    #     with patch('builtins.print') as terminal_print:
    #         self.hostg.create_hostgroup('test_hg1', ['test_host1', 'test_host0'])
    #         terminal_print.assert_called_with('Fail! Can\'t find test_host0.Please give the true name.')
    #     # 创建成功的测试用例
    #     assert self.hostg.create_hostgroup('test_hg1', ['test_host1'])
    #     # self.hostg.show_all_hostgroup()
    #
    # # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    # def test_get_spe_hostgroup(self):
    #     # DiskGroup 不存在
    #     assert not self.hostg.get_spe_hostgroup('test_hg2')
    #     # DiskGroup 存在
    #     assert self.hostg.get_spe_hostgroup('test_hg1')
    #
    # # 该函数没有返回值，调用了本模块get_all_hostgroup()和sundry的show_iscsi_data()
    # def test_show_all_hostgroup(self):
    #     assert self.hostg.show_all_hostgroup() is None
    #
    # # 该函数没有返回值，调用了本模块get_sep_hostgroup()和sundry的show_iscsi_data()
    # def test_show_spe_hostgroup(self):
    #     assert self.hostg.show_spe_hostgroup('test_hg1') is None
    #
    # # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # # 这个方法无返回值
    # def test_delete_hostgroup(self):
    #     with patch('builtins.print') as terminal_print:
    #         self.hostg.delete_hostgroup('test_hg2')
    #         terminal_print.assert_called_with('Fail! Can\'t find test_hg2')
    #     # print(f'判断条件：{self.js.check_value("Map", "test_dg")["result"]}')
    #     # 保留测试用例，该分支有bug
    #     with patch('builtins.print') as terminal_print:
    #         # print(f'判断条件：{self.js.check_value("Map","test_dg")["result"]}')
    #         # self.map.show_all_map()
    #         self.hostg.delete_hostgroup('test_hg')
    #         terminal_print.assert_called_with('Fail! The hostgroup already map,Please delete the map')
    #     with patch('builtins.print') as terminal_print:
    #         self.hostg.delete_hostgroup('test_hg1')
    #         terminal_print.assert_called_with('Delete success!')

    # ------------------- modify ---------------- 2021.01.11
    def test_create(self):
        """创建HostGroup，测试用例包括：HostGroup已存在，创建失败/所配置的 host 不存在，创建失败/创建成功"""
        # 已存在 HostGroup 测试用例
        print('test_hg', self.hostg.show('test_hg'))
        with patch('builtins.print') as terminal_print:
            self.hostg.create('test_hg', ['test_host1'])
            terminal_print.assert_called_with('Fail! The HostGroup test_hg already existed.')
        # 提供的 host 列表中有不存在的 host 测试用例
        with patch('builtins.print') as terminal_print:
            self.hostg.create('test_hg1', ['test_host1', 'test_host0'])
            terminal_print.assert_called_with('Fail! Can\'t find test_host0.Please give the true name.')
        # 创建成功的测试用例
        assert self.hostg.create('test_hg1', ['test_host1'])

    def test_show(self):
        """展示HostGroup"""
        # assert self.hostg.show('all') == [['test_hg', 'test_host1'], ['test_hg1', 'test_host1']]
        assert len(self.hostg.show('all')) >= 1
        assert self.hostg.show('test_hg1') == [['test_hg1', 'test_host1']]
        assert self.hostg.show('test_hg0') == []

    def test_delete(self):
        """删除 HostGroup，测试用例包括：HostGroup不存在，删除失败/已配置在map中，删除失败/删除成功"""
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.hostg.delete('test_hg2')
            terminal_print.assert_called_with('Fail! Can\'t find test_hg2')
        # 已配置在map中
        with patch('builtins.print') as terminal_print:
            self.hostg.delete('test_hg')
            terminal_print.assert_called_with('Fail! The hostgroup already map,Please delete the map')
        # 删除成功
        with patch('builtins.print') as terminal_print:
            self.hostg.delete('test_hg1')
            terminal_print.assert_called_with('Delete success!')

    # --------------------- add  --------------  2020.12.28

    def test_add_host(self):
        """hostgroup 新增 host"""
        # 存在
        assert not self.hostg.add_host('test_hg', ['test_host2'])
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.hostg.add_host('test_hg2', ['test_host2'])
            terminal_print.assert_called_with('Fail！Can\'t find test_hg2')
        with patch('builtins.print') as terminal_print:
            self.hostg.add_host('test_hg', ['test_host1'])
            terminal_print.assert_called_with('test_host1已存在test_hg中')
        with patch('builtins.print') as terminal_print:
            self.hostg.add_host('test_hg', ['test_host0'])
            terminal_print.assert_called_with('json文件中不存在test_host0，无法进行添加')

    def test_remove_host(self):
        """hostgroup 移除 host"""
        # 存在
        assert not self.hostg.remove_host('test_hg', ['test_host2'])
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.hostg.remove_host('test_hg2', ['test_host2'])
            terminal_print.assert_called_with('Fail！Can\'t find test_hg2')
        with patch('builtins.print') as terminal_print:
            self.hostg.remove_host('test_hg', ['test_host0'])
            terminal_print.assert_called_with('test_hg中不存在成员test_host0，无法进行移除')
        # hg 的 host 全部移除，配置了该 hg 的 map 同时被删除
        with patch('builtins.print') as terminal_print:
            self.hostg.remove_host('test_hg', ['test_host1'])
            terminal_print.assert_called_with('相关的map已经修改/删除')

    # # 返回所有 HostGroup，如果为 HostGroup 空，返回{},否则返回 HostGroup 非空字典
    # def test_get_all_hostgroup(self):
    #     # HostGroup 不为空
    #     assert self.hostg.get_all_hostgroup()
    #     # HostGroup 为空
    #     self.map.delete_map('map1')
    #     self.hostg.delete_hostgroup('test_hg')
    #     assert self.hostg.get_all_hostgroup() == {}


class TestMap:

    def setup_class(self):
        # 创建没有被使用过的disk
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        # 配置到没有被使用的diskgroup
        # subprocess.run('python3 vtel.py iscsi dg c test_dg1 res_test1 ', shell=True)
        # # 创建没有被使用的 host
        # subprocess.run('python3 vtel.py iscsi h c test_host1 iqn.2020-04.feixitek.com:pytest0101', shell=True)
        # # 配置到没有被使用的hostgroup
        # subprocess.run('python3 vtel.py iscsi hg c test_hg1 test_host1', shell=True)

        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        # subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest01', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg c test_hg test_host', shell=True)
        # subprocess.run('python3 vtel.py iscsi m c test_map -dg test_dg -hg test_hg', shell=True)
        self.host = iscsi.Host()
        self.hostg = iscsi.HostGroup()
        self.map = iscsi.Map()
        self.diskg = iscsi.DiskGroup()
        self.host.create('test_host1', 'iqn.2020-04.feixitek.com:pytest0101')
        self.host.create('test_host', 'iqn.2020-04.feixitek.com:pytest01')
        self.diskg.create('test_dg1', ['res_test1'])
        self.diskg.create('test_dg', ['res_test'])
        self.hostg.create('test_hg1', ['test_host1'])
        self.hostg.create('test_hg', ['test_host'])
        self.map.create('test_map', ['test_hg'], ['test_dg'])

    def teardown_class(self):
        # subprocess.run('python3 vtel.py iscsi m d test_map -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi hg d test_hg1 -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi h d test_host1 -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg d test_dg -y', shell=True)
        # subprocess.run('python3 vtel.py iscsi dg d test_dg1 -y', shell=True)
        self.map.delete_map('test_map')
        self.hostg.delete('test_hg')
        self.hostg.delete('test_hg1')
        self.diskg.delete('test_dg1')
        self.diskg.delete('test_dg')
        self.host.delete('test_host')
        self.host.delete('test_host1')

        execute_crm_cmd('crm res stop res_test')
        execute_crm_cmd('crm conf del res_test')
        execute_crm_cmd('crm res stop res_test1')
        execute_crm_cmd('crm conf del res_test1')
        subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)

        subprocess.run('python3 vtel.py iscsi d s', shell=True)


    # 函数已修改
    # # 1.map 是否存在/hostgroup是否存在/diskgroup是否存在
    # def test_pre_check_create_map(self):
    #     # map 已存在
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.map.pre_check_create_map('test_map', 'test_hg1', 'test_dg')
    #             terminal_print.assert_called_with('The Map "test_map" already existed.')
    #     assert exsinfo.type == SystemExit
    #     # hostgroup 不存在
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.map.pre_check_create_map('test_map1', 'test_hg0', 'test_dg')
    #             terminal_print.assert_called_with('Can\'t find test_hg0')
    #     assert exsinfo.type == SystemExit
    #     # diskgroup 不存在
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.map.pre_check_create_map('test_map1', 'test_hg', 'test_dg0')
    #             terminal_print.assert_called_with('Can\'t find test_dg0')
    #     assert exsinfo.type == SystemExit
    #     # 同时满足三个条件
    #     assert self.map.pre_check_create_map('test_map1', ['test_hg'], ['test_dg'])
    #
    # def test_get_target(self):
    #     # 检测该函数有返回值
    #     assert self.map.get_target() is not None
    #
    # 先调用pre_check_create_map()，这个函数已经在前面测试了
    # Q：已经被使用过的disk(ilu) 没有做处理？ A:已经被使用的disk 再映射到新的host会提示
    # 1.新建一个map，使用的是没有被使用的disk   create_iscsilogicalunit 没有对创建 iscsilogicalunit 失败做处理
    # 2.新建一个map，使用的是已经被使用的disk并映射到新的host上面
    # 3.同时符合以上两种条件内容的新建map
    # def test_create_map(self):
    #     # 1.使用的是没有被使用的disk，调用 create_iscsilogicalunit，
    #     assert self.map.create_map('test_map1', ['test_hg'], ['test_dg'])
    #     # 2.使用的是已经被使用的disk并映射到新的host上面 调用 modify_iscsilogicalunit 这里会满足提示分支
    #     print('提示分支')
    #     assert self.map.create_map('test_map2', ['test_hg1'], ['test_dg'])
    #     # 3.同时符合以上两种条件内容的新建map
    #     assert self.map.create_map('test_map3', ['test_hg1'], ['test_dg', 'test_dg1'])
    #
    # # map 是否存在，存在返回非空列表[{map: map_data}, list_hg, list_dg],不存在返回 None
    # def test_get_spe_map(self):
    #     # 不存在
    #     with pytest.raises(SystemExit) as exsinfo:
    #         with patch('builtins.print') as terminal_print:
    #             self.map.get_spe_map('test_map0')
    #             terminal_print.assert_called_with('No map data')
    #     assert exsinfo.type == SystemExit
    #     # 存在
    #     assert self.map.get_spe_map('test_map1')
    #
    # # 该函数没有返回值，调用了本模块get_all_map()和sundry的show_iscsi_data()
    # def test_show_all_map(self):
    #     assert self.map.show_all_map() is None
    #
    # def test_show_spe_map(self):
    #     assert self.map.show_spe_map('test_map1') is not None
    #
    # # 1.map 存在返回 True，不存在返回 None
    # def test_pre_check_delete_map(self):
    #     # 不存在,warning_level = 1
    #     assert not self.map.pre_check_delete_map('test_map0')
    #     # 存在
    #     assert self.map.pre_check_delete_map('test_map1')

    # ------- add -------   2020.12.18

    # 函数已修改
    # # 检查列表的每个成员hg/dg是否存在
    # def test_checkout_exist(self):
    #     # 调用 js 中的函数
    #     # 这里不使用 not 的原因是看不出返回值是False/None
    #     # 1.'HostGroup'类别，hg不存在
    #     assert self.map.checkout_exist('HostGroup', ['test_hg1', 'test_hg0']) is False
    #     # 1.'HostGroup'类别，hg存在
    #     assert self.map.checkout_exist('HostGroup', ['test_hg', 'test_hg1']) is None
    #     # 1.'DiskGroup'类别，hg不存在
    #     assert self.map.checkout_exist('DiskGroup', ['test_dg', 'test_dg0']) is False
    #     # 1.'DiskGroup'类别，dg存在
    #     assert self.map.checkout_exist('DiskGroup', ['test_dg', 'test_dg1']) is None

    # ----------modify ----------- 2021.01.11
    def test_create(self):
        # 创建失败
        # map 已存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.create('test_map', 'test_hg1', 'test_dg')
                terminal_print.assert_called_with('The Map "test_map" already existed.')
        assert exsinfo.type == SystemExit
        # hostgroup 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.create('test_map1', 'test_hg0', 'test_dg')
                terminal_print.assert_called_with('Can\'t find test_hg0')
        assert exsinfo.type == SystemExit
        # diskgroup 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.create('test_map1', 'test_hg', 'test_dg0')
                terminal_print.assert_called_with('Can\'t find test_dg0')
        assert exsinfo.type == SystemExit
        # 创建成功
        # 1.使用的是没有被使用的disk，调用 create_iscsilogicalunit，
        assert self.map.create('test_map1', ['test_hg'], ['test_dg'])
        # 2.使用的是已经被使用的disk并映射到新的host上面 调用 modify_iscsilogicalunit 这里会满足提示分支
        assert self.map.create('test_map2', ['test_hg1'], ['test_dg'])
        # 3.同时符合以上两种条件内容的新建map
        assert self.map.create('test_map3', ['test_hg1'], ['test_dg', 'test_dg1'])

    def test_show(self):
        # assert self.map.show('all') == [['test_map', 'test_hg', 'test_dg'], ['test_map1', 'test_hg', 'test_dg'],
        #                                 ['test_map2', 'test_hg1', 'test_dg'],
        #                                 ['test_map3', 'test_hg1', 'test_dg test_dg1']]
        assert len(self.map.show('all')) >= 1
        assert self.map.show('test_map3') == [['test_map3', 'test_hg1', 'test_dg test_dg1']]
        assert self.map.show('test_map0') == []

    # 1.使用pre_check_delete_map检查，map 不存在返回 None，删除成功返回 True
    def test_delete_map(self):
        # 不存在
        with pytest.raises(SystemExit) as exsinfo:
            self.map.delete_map('test_map0')
        assert exsinfo.type == SystemExit
        # 删除成功
        assert self.map.delete_map('test_map3')

    # map modify -hg -a 调用
    def test_add_hg(self):
        # 成功增加
        assert self.map.add_hg('test_map1', ['test_hg1']) is None
        # 1.map 不存在
        with patch('builtins.print') as terminal_print:
            self.map.add_hg('map0', ['test_hg1'])
            terminal_print.assert_called_with('Fail！Can\'t find map0')
        # 2.hg 已存在 map 中
        with patch('builtins.print') as terminal_print:
            self.map.add_hg('test_map1', ['test_hg'])
            terminal_print.assert_called_with('test_hg已存在test_map1中')
        # 3.hg 不存在 json 文件中
        with patch('builtins.print') as terminal_print:
            self.map.add_hg('test_map1', ['test_hg0'])
            terminal_print.assert_called_with('json文件中不存在test_hg0，无法进行添加')

    # map modify -dg -a 调用
    # 1.map 是否存在
    # 2. dg 是否已存在在 map 中/ dg 是否存在 json 文件中
    def test_add_dg(self):
        # 成功增加
        assert self.map.add_dg('test_map2', ['test_dg1']) is None
        # 1.map 不存在
        with patch('builtins.print') as terminal_print:
            self.map.add_dg('map0', ['test_dg1'])
            terminal_print.assert_called_with('Fail！Can\'t find map0')
        # 2.hg 已存在 map 中
        with patch('builtins.print') as terminal_print:
            self.map.add_dg('test_map2', ['test_dg'])
            terminal_print.assert_called_with('test_dg已存在test_map2中')
        # 3.hg 不存在 json 文件中
        with patch('builtins.print') as terminal_print:
            self.map.add_dg('test_map2', ['test_dg0'])
            terminal_print.assert_called_with('json文件中不存在test_dg0，无法进行添加')

    # map modify -hg -r 调用
    # 1.map 是否存在
    # 2.hg 是否存在于该 map 中
    def test_remove_hg(self):
        # 1.map 不存在
        with patch('builtins.print') as terminal_print:
            self.map.remove_hg('map0', ['test_hg1'])
            terminal_print.assert_called_with('Fail！Can\'t find map0')
        with patch('builtins.print') as terminal_print:
            self.map.remove_hg('test_map1', ['test_hg0'])
            terminal_print.assert_called_with('test_map1中不存在成员test_hg0，无法进行移除')
        # 成功移除
        # 移除 map 中 HostGroup 的某些 hg 值，该 map 不会被删除
        self.map.remove_hg('test_map1', ['test_hg'])
        list_hg = self.map.show('test_map1')[0][1]
        assert list_hg == 'test_hg1'
        # 移除 map 中 HostGroup 的全部 hg 值，该 map 被删除
        with patch('builtins.print') as terminal_print:
            self.map.remove_hg('test_map1', ['test_hg1'])
            terminal_print.assert_called_with('该test_map1已删除')

    # map modify -dg -r 调用
    # 1.map 是否存在
    # 2.dg 是否存在于该 map 中
    def test_remove_dg(self):
        # 1.map 不存在
        with patch('builtins.print') as terminal_print:
            self.map.remove_dg('map0', ['test_dg1'])
            terminal_print.assert_called_with('Fail！Can\'t find map0')
        with patch('builtins.print') as terminal_print:
            self.map.remove_dg('test_map2', ['test_dg0'])
            terminal_print.assert_called_with('test_map2中不存在成员test_dg0，无法进行移除')
        # 成功移除
        # 移除 map 中 HostGroup 的某些 dg 值，该 map 不会被删除
        self.map.remove_dg('test_map2', ['test_dg'])
        list_dg = self.map.show('test_map2')[0][2]
        assert list_dg == 'test_dg1'
        # 移除 map 中 HostGroup 的全部 dg 值，该 map 被删除
        with patch('builtins.print') as terminal_print:
            self.map.remove_dg('test_map2', ['test_dg1'])
            terminal_print.assert_called_with('该test_map2已删除')

    # # 获取 map 并返回，map 为空返回 {},不为空返回非空字典
    # def test_get_all_map(self):
    #     # map 不为空
    #     assert self.map.create('test_map3', ['test_hg1'], ['test_dg', 'test_dg1'])
    #     assert self.map.get_all_map()
    #     # map 为空
    #     # self.map.delete_map('test_map1')
    #     # self.map.delete_map('test_map2')
    #     self.map.delete_map('test_map3')
    #     time.sleep(1)
    #     assert self.map.get_all_map() == {}

    # 该函数被其他函数调用 create_iSCSILogicalUnit


@pytest.mark.portal
class TestPortal:
    # 注意测试用例 IP 不能是本机 ip 10.201.3.76
    def setup_class(self):
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi sync', shell=True)
        self.portal = iscsi.Portal()
        # print(self.portal.js.read_json())
        self.portal.create('vip_test1', '10.203.1.210')

    def teardown_class(self):
        print()
        # 以防删除不成功再次删除
        self.portal.delete('vip_test1')

    def test_create(self):
        """创建portal，测试用例包括：(名字不合规范/ip不合规范/port超出范围/netmark超出范围[已测试其校验函数])portal已存在/ip已被使用"""
        with patch('builtins.print') as terminal_print:
            self.portal.create('$%^vip_test1', '10.203.1.211', 3260, 24)
            terminal_print.assert_called_with('$%^vip_test1 naming does not conform to the specification')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_test0', '10.203.1...34211', 3260, 24)
            terminal_print.assert_called_with('10.203.1...34211 does not meet specifications')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_test0', '10.203.1.211', 65555, 24)
            terminal_print.assert_called_with('65555 does not meet specifications(Range：3260-65535)')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_test0', '10.203.1.211', 3260, 40)
            terminal_print.assert_called_with('40 does not meet specifications(Range：1-32)')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_test1', '10.203.1.211', 3260, 24)
            terminal_print.assert_called_with('vip_test1 already exists, please use another name')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_pytest', '10.203.1.210')
            terminal_print.assert_called_with('10.203.1.210 is already in use, please use another IP')
        with patch('builtins.print') as terminal_print:
            self.portal.create('vip_pytest', '10.203.1.211')
            terminal_print.assert_called_with('Create vip_pytest successfully')
        # self.portal.delete('vip_pytest')

    def test_modify(self):
        """修改 portal,测试用例包括：portal不存在/ip格式不对正确/port范围不正确/修改内容与原来一致/修改的portal已配置了target/修改的portal没有配置target"""
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip_pytest0', '10.203.1.212', 3260)
            terminal_print.assert_called_with('Fail！Can\'t find vip_pytest0')
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip_pytest', '10.203.1.75', 3260)
            terminal_print.assert_called_with('10.203.1.75 is already in use, please use another IP')
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip', '10.203.1.212...', 3260)
            terminal_print.assert_called_with('10.203.1.212... does not meet specifications')
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip', '10.203.1.212', 3200)
            terminal_print.assert_called_with('3200 does not meet specifications(Range：3260-65535)')
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip', '10.203.1.75', 3260)
            terminal_print.assert_called_with('IP and port are the same as the before, no need to modify')
        # 修改的portal已配置了target，修改portblk的时候注意命名是否能找到
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip_test2', '10.203.1.205', 3260)
            # terminal_print.assert_called_with('Modify target_test successfully')
            terminal_print.assert_called_with('Modify vip_test2 successfully')
        with patch('builtins.print') as terminal_print:
            self.portal.modify('vip_pytest', '10.203.1.214', 3260)
            terminal_print.assert_called_with('Modify vip_pytest successfully')

        self.portal.modify('vip_test2', '10.203.1.206', 3260)
        self.portal.delete('vip_pytest')

    def test__check_status(self):
        """检查 portal 创建的 status，测试用例包括：portal状态正常/portal状态异常"""
        with patch('builtins.print') as terminal_print:
            assert self.portal._check_status('vip') == 'OK'
            terminal_print.assert_called_with('Create vip successfully')
        # vip_pytest 已删除的情况下
        with patch('builtins.print') as terminal_print:
            self.portal._check_status('vip_pytest')
            terminal_print.assert_called_with('Failed to create vip_pytest, please check')

    def test_delete(self):
        """删除portal，测试用例包括：portal不存在/删除已配置target的portal，删除失败/删除成功"""
        with patch('builtins.print') as terminal_print:
            self.portal.delete('vip_pytest')
        terminal_print.assert_called_with('Fail！Can\'t find vip_pytest')
        with patch('builtins.print') as terminal_print:
            self.portal.delete('vip_test1')
        terminal_print.assert_called_with('Delete vip_test1 successfully')
        with patch('builtins.print') as terminal_print:
            self.portal.delete('vip')
        terminal_print.assert_called_with('In use：t_test. Can not delete')

    def test_show(self):
        """展示全部 portal"""
        # print(self.portal.show())
        assert len(self.portal.show()) >= 1

        # 格式要求：必须以字母开头，只能包含字母、数字、下划线_

    def test__check_name(self):
        """检查 portal_name，测试用例包括：不以字母开头/包含其他字符/包含中文字符/正确命名"""
        assert self.portal._check_name('sgfbfuhf')
        assert not self.portal._check_name('_sgfbfuhf')
        assert not self.portal._check_name('7_sgfbfuhf')
        assert not self.portal._check_name('sgfb*f$uhf')
        assert not self.portal._check_name('sgfbf你uhf')

    def test__check_ip(self):
        """检查 ip 格式，测试用例包括：包含其他字符/格式不正确/正确命名"""
        assert not self.portal._check_IP('10.11.11..11')
        assert not self.portal._check_IP('.10.11.11.11')
        assert not self.portal._check_IP('10.11.11.ss')
        assert self.portal._check_IP('10.11.11.10')

    def test__check_port(self):
        """检查 port 范围，测试用例包括：大于3620/等于3260/小于3260/非int"""
        assert self.portal._check_port(3260)
        assert not self.portal._check_port(3259)
        assert self.portal._check_port(3261)
        assert self.portal._check_port(65535)
        assert not self.portal._check_port(65536)
        assert not self.portal._check_port('6s55')

    def test__check_netmask(self):
        """检查 port 范围，测试用例包括：小于0/等于0/小于32/等于32/大于32/非int"""
        assert not self.portal._check_netmask(-1)
        assert not self.portal._check_netmask(0)
        assert self.portal._check_netmask(32)
        assert self.portal._check_netmask(31)
        assert not self.portal._check_netmask(33)
        assert not self.portal._check_netmask('3s')
