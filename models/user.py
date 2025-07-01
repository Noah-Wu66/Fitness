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
            'updated_at': datetime.utcnow(),
            # 用户个人信息字段
            'profile': {
                'nickname': '',
                'gender': '',  # 'male', 'female'
                'age': None,
                'height': None,  # 厘米
                'weight': None,  # 公斤
                'target_weight': None,  # 目标体重（公斤）
                'avatar': '',  # 头像URL
                'daily_calorie_goal': None,  # 每日热量目标
                'activity_level': 'moderate',  # 活动水平: sedentary, light, moderate, active, very_active
                'goal_type': 'maintain'  # 目标类型: lose, maintain, gain
            },
            'profile_completed': False  # 是否完成了个人信息设置
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
                    'is_admin': user.get('is_admin', False),
                    'profile': user.get('profile', {}),
                    'profile_completed': user.get('profile_completed', False)
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

    def update_user_profile(self, user_id, profile_data):
        """更新用户个人信息"""
        try:
            # 验证个人信息数据
            validation_result = self.validate_profile_data(profile_data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}

            # 计算每日热量目标
            daily_calorie_goal = self.calculate_daily_calories(profile_data)
            profile_data['daily_calorie_goal'] = daily_calorie_goal

            # 更新用户信息
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'profile': profile_data,
                        'profile_completed': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                return {'success': True, 'daily_calorie_goal': daily_calorie_goal}
            else:
                return {'success': False, 'error': '更新失败'}

        except Exception as e:
            return {'success': False, 'error': f'更新失败: {str(e)}'}

    def validate_profile_data(self, profile_data):
        """验证个人信息数据"""
        required_fields = ['nickname', 'gender', 'age', 'height', 'weight']

        for field in required_fields:
            if not profile_data.get(field):
                return {'valid': False, 'error': f'{field} 不能为空'}

        # 验证数值范围
        age = profile_data.get('age')
        if not isinstance(age, int) or age < 10 or age > 120:
            return {'valid': False, 'error': '年龄必须在10-120之间'}

        height = profile_data.get('height')
        if not isinstance(height, (int, float)) or height < 100 or height > 250:
            return {'valid': False, 'error': '身高必须在100-250厘米之间'}

        weight = profile_data.get('weight')
        if not isinstance(weight, (int, float)) or weight < 30 or weight > 300:
            return {'valid': False, 'error': '体重必须在30-300公斤之间'}

        target_weight = profile_data.get('target_weight')
        if target_weight and (not isinstance(target_weight, (int, float)) or target_weight < 30 or target_weight > 300):
            return {'valid': False, 'error': '目标体重必须在30-300公斤之间'}

        gender = profile_data.get('gender')
        if gender not in ['male', 'female']:
            return {'valid': False, 'error': '性别必须是男性或女性'}

        return {'valid': True}

    def calculate_daily_calories(self, profile_data):
        """计算每日热量需求（使用Harris-Benedict公式）"""
        try:
            age = int(profile_data['age'])
            height = float(profile_data['height'])
            weight = float(profile_data['weight'])
            gender = profile_data['gender']
            activity_level = profile_data.get('activity_level', 'moderate')
            goal_type = profile_data.get('goal_type', 'maintain')

            # Harris-Benedict公式计算基础代谢率(BMR)
            if gender == 'male':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

            # 活动水平系数
            activity_multipliers = {
                'sedentary': 1.2,      # 久坐不动
                'light': 1.375,        # 轻度活动
                'moderate': 1.55,      # 中度活动
                'active': 1.725,       # 高度活动
                'very_active': 1.9     # 极高活动
            }

            # 计算总热量需求
            tdee = bmr * activity_multipliers.get(activity_level, 1.55)

            # 根据目标调整热量
            if goal_type == 'lose':
                # 减重：减少500卡路里/天（约每周减重0.5公斤）
                daily_calories = tdee - 500
            elif goal_type == 'gain':
                # 增重：增加500卡路里/天
                daily_calories = tdee + 500
            else:
                # 维持体重
                daily_calories = tdee

            # 确保热量不低于基础代谢率的80%
            min_calories = bmr * 0.8
            daily_calories = max(daily_calories, min_calories)

            return round(daily_calories)

        except Exception as e:
            # 如果计算失败，返回默认值
            return 2000

    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                return {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user.get('is_admin', False),
                    'profile': user.get('profile', {}),
                    'profile_completed': user.get('profile_completed', False)
                }
            return None
        except Exception:
            return None
    
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
