from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from models.user import User
from auth.auth import login_user, logout_user, get_current_user, login_required

def create_auth_blueprint(mongo):
    """创建认证蓝图"""
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
    user_model = User(mongo)
    
    @auth_bp.route('/register', methods=['GET', 'POST'])
    def register():
        """用户注册"""
        if request.method == 'GET':
            # 如果已登录，重定向到首页
            if get_current_user():
                return redirect(url_for('index'))
            return render_template('auth/register.html')
        
        # POST请求处理注册
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # 验证确认密码
        if password != confirm_password:
            error_msg = '两次输入的密码不一致'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('auth/register.html')
        
        # 创建用户
        result = user_model.create_user(username, email, password)
        
        if result['success']:
            if request.is_json:
                return jsonify(result)
            else:
                flash('注册成功，请登录', 'success')
                return redirect(url_for('auth.login'))
        else:
            if request.is_json:
                return jsonify(result), 400
            else:
                flash(result['error'], 'error')
                return render_template('auth/register.html')
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        """用户登录"""
        if request.method == 'GET':
            # 如果已登录，重定向到首页
            if get_current_user():
                return redirect(url_for('index'))
            return render_template('auth/login.html')
        
        # POST请求处理登录
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        login_identifier = data.get('login_identifier', '').strip()
        password = data.get('password', '')
        
        if not login_identifier or not password:
            error_msg = '请输入用户名/邮箱和密码'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('auth/login.html')
        
        # 验证用户
        result = user_model.authenticate_user(login_identifier, password)
        
        if result['success']:
            # 登录成功，设置session
            login_user(result['user'])
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'user': result['user']
                })
            else:
                flash('登录成功', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
        else:
            if request.is_json:
                return jsonify(result), 401
            else:
                flash(result['error'], 'error')
                return render_template('auth/login.html')
    
    @auth_bp.route('/logout', methods=['POST'])
    def logout():
        """用户登出"""
        logout_user()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '已退出登录'})
        else:
            flash('已退出登录', 'info')
            return redirect(url_for('auth.login'))
    
    @auth_bp.route('/admin-register', methods=['GET', 'POST'])
    def admin_register():
        """超级管理员注册"""
        if request.method == 'GET':
            # 如果已登录，重定向到首页
            if get_current_user():
                return redirect(url_for('index'))
            return render_template('auth/admin_register.html')

        # POST请求处理注册
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        admin_key = data.get('admin_key', '').strip()

        # 验证管理员密钥（使用内置密钥）
        correct_admin_key = 'H7jK9mN2pQ5rS8tU1vW4xY7zA0bC3dF6gH9jK2mN5pQ8rS1tU4vW7xY0zA3bC6dF'

        if admin_key != correct_admin_key:
            error_msg = '管理员注册密钥错误'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('auth/admin_register.html')

        # 验证确认密码
        if password != confirm_password:
            error_msg = '两次输入的密码不一致'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('auth/admin_register.html')

        # 创建管理员用户
        result = user_model.create_user(username, email, password)

        if result['success']:
            # 设置为管理员
            from bson import ObjectId
            mongo.db.users.update_one(
                {'_id': ObjectId(result['user_id'])},
                {'$set': {'is_admin': True}}
            )

            if request.is_json:
                return jsonify({'success': True, 'message': '超级管理员注册成功'})
            else:
                flash('超级管理员注册成功，请登录', 'success')
                return redirect(url_for('auth.login'))
        else:
            if request.is_json:
                return jsonify(result), 400
            else:
                flash(result['error'], 'error')
                return render_template('auth/admin_register.html')

    @auth_bp.route('/current_user', methods=['GET'])
    def current_user():
        """获取当前用户信息"""
        user = get_current_user()
        if user:
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'error': '未登录'}), 401

    @auth_bp.route('/setup-profile', methods=['GET', 'POST'])
    @login_required
    def setup_profile():
        """用户信息设置页面"""
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))

        if request.method == 'GET':
            return render_template('auth/user_info_setup.html', user=user)

        # POST请求处理信息保存
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # 转换数值类型
        try:
            if 'age' in data and data['age']:
                data['age'] = int(data['age'])
            if 'height' in data and data['height']:
                data['height'] = float(data['height'])
            if 'weight' in data and data['weight']:
                data['weight'] = float(data['weight'])
            if 'target_weight' in data and data['target_weight']:
                data['target_weight'] = float(data['target_weight'])
            else:
                # 如果目标体重为空，设置为None
                data['target_weight'] = None

            # 确保必填字段不为空
            required_fields = ['nickname', 'gender', 'age', 'height', 'weight']
            for field in required_fields:
                if field not in data or not data[field]:
                    error_msg = f'请填写{field}'
                    if request.is_json:
                        return jsonify({'success': False, 'error': error_msg}), 400
                    else:
                        flash(error_msg, 'error')
                        return render_template('auth/user_info_setup.html', user=user)

        except ValueError:
            error_msg = '请输入有效的数值'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('auth/user_info_setup.html', user=user)

        # 更新用户信息
        result = user_model.update_user_profile(user['id'], data)

        if result['success']:
            # 更新session中的用户信息
            session['profile_completed'] = True
            session['profile'] = data  # 更新profile数据

            # 为了确保数据一致性，重新从数据库获取用户信息
            updated_user = user_model.get_user_by_id(user['id'])

            if updated_user:
                session['profile'] = updated_user.get('profile', {})
                session['profile_completed'] = updated_user.get('profile_completed', False)

            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': '个人信息设置成功',
                    'daily_calorie_goal': result.get('daily_calorie_goal')
                })
            else:
                flash('个人信息设置成功', 'success')
                return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify(result), 400
            else:
                flash(result['error'], 'error')
                return render_template('auth/user_info_setup.html', user=user)

    return auth_bp
