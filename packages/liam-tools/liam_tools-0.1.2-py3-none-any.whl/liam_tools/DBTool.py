import sys
from flask_sqlalchemy import SQLAlchemy
from liam_tools import path

class DbTool:
    def __init__(self, app, appName):

        """
        初始化数据库工具
        :param app: 传入的 Flask 实例
        :param appName: 应用名称用于路径生成
        """
        isWin = sys.platform.startswith('win')
        prefix = 'sqlite:///' if isWin else 'sqlite:////'

        dbPath = path.cache(appName, 'data.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = prefix + dbPath
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = SQLAlchemy(app)

    def initTable(self):
        """创建所有表"""
        with self.db.app.app_context():
            self.db.create_all()
        print('Initialized database.')

    def addRecord(self, bean):
        """添加数据记录"""
        self.db.session.add(bean)

    def queryById(self, modelClass, recordId):
        """根据 ID 查询"""
        return modelClass.query.get(recordId)

    def deleteRecord(self, bean):
        """删除数据记录"""
        self.db.session.delete(bean)

    def flush(self):
        """提交事务，包含错误回滚逻辑"""
        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            print(f"Database commit failed: {e}")

    def updateRecord(self):
        """
        在 SQLAlchemy 中，修改对象属性后直接调用 flush 即可。
        此处仅作为驼峰命名的占位。
        """
        self.flush()