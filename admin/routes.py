from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.user import User
from models.history import History
from auth.auth import admin_required, get_current_user

def create_admin_blueprint(mongo):
    """创建管理员蓝图"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    user_model = User(mongo)
    history_model = History(mongo)
    
    @admin_bp.route('/')
    @admin_required
    def dashboard():
        """管理员仪表板"""
        return render_template('admin/dashboard.html')
    
    @admin_bp.route('/users')
    @admin_required
    def users():
        """用户管理页面"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = user_model.get_all_users(page, per_page)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return render_template('admin/users.html', **result)
    
    @admin_bp.route('/users/<user_id>')
    @admin_required
    def user_detail(user_id):
        """用户详情页面"""
        user = user_model.get_user_by_id(user_id)
        if not user:
            if request.is_json:
                return jsonify({'success': False, 'error': '用户不存在'}), 404
            else:
                flash('用户不存在', 'error')
                return redirect(url_for('admin.users'))
        
        # 获取用户统计信息
        stats_result = history_model.get_user_statistics(user_id)
        statistics = stats_result.get('statistics', {}) if stats_result['success'] else {}
        
        # 获取用户最近的历史记录
        history_result = history_model.get_user_history(user_id, page=1, per_page=10)
        recent_history = history_result.get('history', []) if history_result['success'] else []
        
        if request.is_json:
            return jsonify({
                'success': True,
                'user': user,
                'statistics': statistics,
                'recent_history': recent_history
            })
        else:
            return render_template('admin/user_detail.html', 
                                 user=user, 
                                 statistics=statistics,
                                 recent_history=recent_history)
    
    @admin_bp.route('/users/<user_id>/toggle_status', methods=['POST'])
    @admin_required
    def toggle_user_status(user_id):
        """切换用户状态（启用/禁用）"""
        current_user = get_current_user()
        
        # 防止管理员禁用自己
        if current_user['id'] == user_id:
            error_msg = '不能禁用自己的账号'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return redirect(url_for('admin.user_detail', user_id=user_id))
        
        user = user_model.get_user_by_id(user_id)
        if not user:
            error_msg = '用户不存在'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 404
            else:
                flash(error_msg, 'error')
                return redirect(url_for('admin.users'))
        
        new_status = not user['is_active']
        success = user_model.update_user_status(user_id, new_status)
        
        if success:
            status_text = '启用' if new_status else '禁用'
            message = f'用户已{status_text}'
            if request.is_json:
                return jsonify({'success': True, 'message': message})
            else:
                flash(message, 'success')
        else:
            error_msg = '操作失败'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
        
        if not request.is_json:
            return redirect(url_for('admin.user_detail', user_id=user_id))
    
    @admin_bp.route('/users/<user_id>/delete', methods=['POST'])
    @admin_required
    def delete_user(user_id):
        """删除用户"""
        current_user = get_current_user()
        
        # 防止管理员删除自己
        if current_user['id'] == user_id:
            error_msg = '不能删除自己的账号'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return redirect(url_for('admin.user_detail', user_id=user_id))
        
        user = user_model.get_user_by_id(user_id)
        if not user:
            error_msg = '用户不存在'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 404
            else:
                flash(error_msg, 'error')
                return redirect(url_for('admin.users'))
        
        success = user_model.delete_user(user_id)
        
        if success:
            message = '用户已删除'
            if request.is_json:
                return jsonify({'success': True, 'message': message})
            else:
                flash(message, 'success')
                return redirect(url_for('admin.users'))
        else:
            error_msg = '删除失败'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return redirect(url_for('admin.user_detail', user_id=user_id))
    
    @admin_bp.route('/statistics')
    @admin_required
    def statistics():
        """系统统计信息"""
        try:
            # 获取用户统计
            total_users = mongo.db.users.count_documents({})
            active_users = mongo.db.users.count_documents({'is_active': True})
            admin_users = mongo.db.users.count_documents({'is_admin': True})

            # 获取历史记录统计
            total_analyses = mongo.db.history.count_documents({})

            # 最近30天的分析次数
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_analyses = mongo.db.history.count_documents({
                'created_at': {'$gte': thirty_days_ago}
            })

            stats = {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'admin': admin_users,
                    'inactive': total_users - active_users
                },
                'analyses': {
                    'total': total_analyses,
                    'recent_30_days': recent_analyses
                }
            }

            if request.is_json:
                return jsonify({'success': True, 'statistics': stats})
            else:
                return render_template('admin/statistics.html', statistics=stats)

        except Exception as e:
            error_msg = f'获取统计信息失败: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return render_template('admin/statistics.html', statistics={
                    'users': {'total': 0, 'active': 0, 'admin': 0, 'inactive': 0},
                    'analyses': {'total': 0, 'recent_30_days': 0}
                })
    
    return admin_bp
