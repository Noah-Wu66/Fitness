from flask import Blueprint, request, jsonify
from models.history import History
from auth.auth import login_required, get_current_user

def create_history_blueprint(mongo):
    """创建历史记录API蓝图"""
    history_bp = Blueprint('history_api', __name__, url_prefix='/api/history')
    history_model = History(mongo)
    
    @history_bp.route('/', methods=['GET'])
    @login_required
    def get_history():
        """获取用户历史记录"""
        user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = history_model.get_user_history(user['id'], page, per_page)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @history_bp.route('/', methods=['POST'])
    @login_required
    def save_history():
        """保存分析记录"""
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '无效的请求数据'}), 400
        
        image_data = data.get('image_data')
        analysis_result = data.get('analysis_result')
        usage_info = data.get('usage_info')
        
        if not all([image_data, analysis_result, usage_info]):
            return jsonify({'success': False, 'error': '缺少必要的数据字段'}), 400
        
        result = history_model.save_analysis(
            user['id'], 
            image_data, 
            analysis_result, 
            usage_info
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @history_bp.route('/<history_id>', methods=['DELETE'])
    @login_required
    def delete_history_item(history_id):
        """删除单条历史记录"""
        user = get_current_user()
        
        success = history_model.delete_history_item(user['id'], history_id)
        
        if success:
            return jsonify({'success': True, 'message': '记录已删除'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500
    
    @history_bp.route('/clear', methods=['POST'])
    @login_required
    def clear_history():
        """清空用户历史记录"""
        user = get_current_user()
        
        result = history_model.clear_user_history(user['id'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @history_bp.route('/statistics', methods=['GET'])
    @login_required
    def get_statistics():
        """获取用户统计信息"""
        user = get_current_user()
        
        result = history_model.get_user_statistics(user['id'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    return history_bp
