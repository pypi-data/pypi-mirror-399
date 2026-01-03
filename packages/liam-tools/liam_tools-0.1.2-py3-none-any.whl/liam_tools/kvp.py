from dbm import open
from os import path as ospath
from liam_tools import pl, path

class Kvp:
    """
    基于 dbm 的 Key-Value 存储工具类
    """
    def __init__(self, fileName: str):
        # 使用 os.path 提升路径兼容性
        self.dbDir = ospath.join(path.curDir(), 'db')
        path.mkfolder(self.dbDir)
        self.dbPath = ospath.join(self.dbDir, fileName)

    def insert(self, key: str, value: str):
        """新增或更新数据"""
        try:
            with open(self.dbPath, 'c') as db:
                db[key] = value
        except Exception as e:
            pl.w(f"Insert failed: {e}")

    def delete(self, key: str):
        """删除指定的 key"""
        try:
            with open(self.dbPath, 'c') as db:
                if key in db:
                    del db[key]
        except Exception as e:
            pl.w(f"Delete failed: {e}")

    def update(self, key: str, value: str):
        """修改数据（逻辑等同于插入）"""
        self.insert(key, value)

    def select(self, key: str):
        """查询数据，若不存在返回 None"""
        try:
            with open(self.dbPath, 'c') as db:
                # dbm 返回的是 bytes 类型，视需求决定是否 decode
                value = db.get(key)
                return value.decode('utf-8') if value else None
        except Exception as e:
            pl.w(f"Select failed: {e}")
            return None

    def getKeys(self):
        """获取所有 key 列表"""
        try:
            with open(self.dbPath, 'c') as db:
                return db.keys()
        except Exception as e:
            pl.w(f"Get keys failed: {e}")
            return []

# --- 测试用例 ---
if __name__ == "__main__":
    # 类名改用 PascalCase，实例用 lowerCamelCase
    kvm = Kvp('token')

    # 测试插入与查询
    kvm.insert('myKey', 'hello_world')
    pl.i(f"Keys: {kvm.getKeys()}")
    pl.i(f"Value: {kvm.select('myKey')}")

    # 测试更新
    kvm.update('myKey', 'new_value')
    pl.i(f"Updated Value: {kvm.select('myKey')}")

    # 测试删除
    kvm.deleteKey('myKey')
    pl.i(f"After Delete: {kvm.select('myKey')}")