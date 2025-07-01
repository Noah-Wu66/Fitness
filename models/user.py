import bcrypt
from datetime import datetime
from bson import ObjectId
import re
from email_validator import validate_email, EmailNotValidError

class User:
    """用户模型类"""
    
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.users
    
    def create_user(self, username, email, password):
        """创建新用户"""
        # 验证输入
        validation_result = self.validate_user_data(username, email, password)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['error']}
        
        # 检查用户名和邮箱是否已存在
        if self.collection.find_one({'username': username}):
            return {'success': False, 'error': '用户名已存在'}
        
        if self.collection.find_one({'email': email}):
            return {'success': False, 'error': '邮箱已被注册'}
        
        # 加密密码
        hashed_password = self.hash_password(password)
        
        # 创建用户文档
        user_doc = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'is_active': True,
            'is_admin': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(user_doc)
            return {
                'success': True,
                'user_id': str(result.inserted_id),
                'message': '用户创建成功'
            }
        except Exception as e:
            return {'success': False, 'error': f'创建用户失败: {str(e)}'}
    
    def authenticate_user(self, login_identifier, password):
        """用户认证（支持用户名或邮箱登录）"""
        # 查找用户（用户名或邮箱）
        user = self.collection.find_one({
            '$or': [
                {'username': login_identifier},
                {'email': login_identifier}
            ]
        })
        
        if not user:
            return {'success': False, 'error': '用户不存在'}
        
        if not user.get('is_active', True):
            return {'success': False, 'error': '账号已被禁用'}
        
        # 验证密码
        if self.verify_password(password, user['password']):
            return {
                'success': True,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user.get('is_admin', False)
                }
            }
        else:
            return {'success': False, 'error': '密码错误'}
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                return {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'is_active': user.get('is_active', True),
                    'is_admin': user.get('is_admin', False),
                    'created_at': user.get('created_at')
                }
            return None
        except Exception:
            return None
    
    def get_all_users(self, page=1, per_page=20):
        """获取所有用户列表（分页）"""
        skip = (page - 1) * per_page
        
        users = list(self.collection.find(
            {},
            {'password': 0}  # 不返回密码字段
        ).skip(skip).limit(per_page).sort('created_at', -1))
        
        total = self.collection.count_documents({})
        
        # 转换ObjectId为字符串
        for user in users:
            user['id'] = str(user['_id'])
            del user['_id']
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def update_user_status(self, user_id, is_active):
        """更新用户状态（启用/禁用）"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'is_active': is_active,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            # 同时删除用户的历史记录
            self.mongo.db.history.delete_many({'user_id': user_id})
            
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    @staticmethod
    def hash_password(password):
        """加密密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    @staticmethod
    def validate_user_data(username, email, password):
        """验证用户数据"""
        # 验证用户名
        if not username or len(username) < 3 or len(username) > 20:
            return {'valid': False, 'error': '用户名长度必须在3-20个字符之间'}
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            return {'valid': False, 'error': '用户名只能包含字母、数字、下划线和中文字符'}
        
        # 验证邮箱
        try:
            validate_email(email)
        except EmailNotValidError:
            return {'valid': False, 'error': '邮箱格式不正确'}
        
        # 验证密码
        if not password or len(password) < 6:
            return {'valid': False, 'error': '密码长度至少6个字符'}
        
        if len(password) > 128:
            return {'valid': False, 'error': '密码长度不能超过128个字符'}
        
        return {'valid': True}
