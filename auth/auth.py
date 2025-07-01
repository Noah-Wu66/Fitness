from functools import wraps
from flask import session, request, jsonify, redirect, url_for

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': '请先登录', 'login_required': True}), 401
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': '请先登录', 'login_required': True}), 401
            else:
                return redirect(url_for('auth.login'))
        
        if not session.get('is_admin', False):
            if request.is_json:
                return jsonify({'error': '需要管理员权限'}), 403
            else:
                return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session.get('username'),
            'email': session.get('email'),
            'is_admin': session.get('is_admin', False),
            'profile': session.get('profile', {}),
            'profile_completed': session.get('profile_completed', False)
        }
    return None

def login_user(user_data):
    """用户登录，设置session"""
    session['user_id'] = user_data['id']
    session['username'] = user_data['username']
    session['email'] = user_data['email']
    session['is_admin'] = user_data.get('is_admin', False)
    session['profile'] = user_data.get('profile', {})
    session['profile_completed'] = user_data.get('profile_completed', False)
    session.permanent = True

def logout_user():
    """用户登出，清除session"""
    session.clear()
