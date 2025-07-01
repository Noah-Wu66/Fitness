import os
from pymongo import MongoClient
from flask_pymongo import PyMongo

class DatabaseConfig:
    """数据库配置类"""
    
    @staticmethod
    def get_mongo_uri():
        """获取MongoDB连接URI"""
        # 优先使用完整的连接字符串
        mongodb_uri = os.getenv('MONGODB_URI') or os.getenv('DATABASE_URL')
        if mongodb_uri:
            return mongodb_uri

        # 回退到分离式配置
        mongo_host = os.getenv('MONGO_HOST', 'localhost')
        mongo_port = os.getenv('MONGO_PORT', '27017')
        mongo_db = os.getenv('MONGO_DB', 'fitness_app')
        mongo_username = os.getenv('MONGO_USERNAME')
        mongo_password = os.getenv('MONGO_PASSWORD')

        # 构建连接URI
        if mongo_username and mongo_password:
            uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
        else:
            uri = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"

        return uri
    
    @staticmethod
    def init_app(app):
        """初始化数据库连接"""
        app.config['MONGO_URI'] = DatabaseConfig.get_mongo_uri()
        mongo = PyMongo(app)
        
        # 创建索引
        DatabaseConfig.create_indexes(mongo)
        
        return mongo
    
    @staticmethod
    def create_indexes(mongo):
        """创建数据库索引"""
        try:
            # 用户集合索引
            mongo.db.users.create_index("username", unique=True)
            mongo.db.users.create_index("email", unique=True)
            
            # 历史记录集合索引
            mongo.db.history.create_index([("user_id", 1), ("created_at", -1)])
            
            print("数据库索引创建成功")
        except Exception as e:
            print(f"创建索引时出错: {e}")
