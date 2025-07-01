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
            # 检查连接字符串是否包含数据库名
            return DatabaseConfig._ensure_database_name(mongodb_uri)

        # 回退到分离式配置
        mongo_host = os.getenv('MONGO_HOST', 'localhost')
        mongo_port = os.getenv('MONGO_PORT', '27017')
        mongo_db = os.getenv('MONGO_DB', 'fitness_app')
        mongo_username = os.getenv('MONGO_USERNAME')
        mongo_password = os.getenv('MONGO_PASSWORD')

        # 构建连接URI
        if mongo_username and mongo_password:
            uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
            
            # 处理可选的 authSource 与其他参数
            query_params = []
            mongo_auth_source = os.getenv('MONGO_AUTH_SOURCE')  # 认证数据库，常见为 admin
            if mongo_auth_source:
                query_params.append(f"authSource={mongo_auth_source}")
            # 允许通过 MONGO_OPTIONS 追加其它自定义参数，如 retryWrites=true&w=majority
            mongo_extra_opts = os.getenv('MONGO_OPTIONS')
            if mongo_extra_opts:
                # 支持用分号或逗号分隔的键值对列表
                cleaned_opts = mongo_extra_opts.replace(';', '&').replace(',', '&')
                query_params.append(cleaned_opts)
            if query_params:
                uri += '?' + '&'.join(query_params)
        else:
            uri = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"

        return uri

    @staticmethod
    def _ensure_database_name(mongodb_uri, default_db='fitness_app'):
        """确保MongoDB连接字符串包含数据库名"""
        try:
            # 解析连接字符串
            if '?' in mongodb_uri:
                # 处理包含查询参数的情况
                base_uri, query_params = mongodb_uri.split('?', 1)
                query_suffix = f'?{query_params}'
            else:
                base_uri = mongodb_uri
                query_suffix = ''

            # 检查是否已包含数据库名
            # 格式：mongodb://user:pass@host:port/database 或 mongodb+srv://user:pass@host/database
            if base_uri.count('/') >= 3:
                # 已包含数据库名，检查是否为空
                parts = base_uri.split('/')
                if len(parts) > 3 and parts[3].strip():
                    # 数据库名不为空，返回原字符串
                    return mongodb_uri
                else:
                    # 数据库名为空，替换为默认数据库名
                    parts[3] = default_db
                    return '/'.join(parts) + query_suffix
            else:
                # 不包含数据库名，添加默认数据库名
                return f"{base_uri}/{default_db}{query_suffix}"

        except Exception as e:
            # 解析失败时，尝试简单添加数据库名
            print(f"警告: MongoDB URI解析失败，使用简单方式添加数据库名: {e}")
            if mongodb_uri.endswith('/'):
                return f"{mongodb_uri}{default_db}"
            else:
                return f"{mongodb_uri}/{default_db}"
    
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
