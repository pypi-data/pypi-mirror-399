# 全局变量

class GlobalState:
    def __init__(self):
        self.level = 1
        self.family = "ipv6"
        self.topo_path = "agent/route/tools/data/topology_test.json"
        self.system_id = "0000.0000.0001.00"
        self.system_index = 0

    def set_path(self, level, family, topo_path, sys_id, sys_index):
        self.level = level
        self.family = family
        self.topo_path = topo_path
        self.system_id = sys_id
        self.system_index = sys_index

    def get_path(self):
        return self.level, self.family, self.topo_path, self.sys_id, self.sys_index


def set_global_path(level, family, topo_path, sys_id, sys_index):
    GLOBAL_STATE.set_path(level, family, topo_path, sys_id, sys_index)


def get_global_path():
    return GLOBAL_STATE.get_path()


GLOBAL_STATE = GlobalState()
