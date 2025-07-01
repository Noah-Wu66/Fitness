from datetime import datetime
from bson import ObjectId

class History:
    """历史记录模型类"""
    
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.history
    
    def save_analysis(self, user_id, image_data, analysis_result, usage_info):
        """保存分析记录"""
        history_doc = {
            'user_id': user_id,
            'image_data': image_data,  # Base64编码的图片数据
            'analysis_result': analysis_result,
            'usage_info': usage_info,
            'created_at': datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(history_doc)
            return {
                'success': True,
                'history_id': str(result.inserted_id)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'保存历史记录失败: {str(e)}'
            }
    
    def get_user_history(self, user_id, page=1, per_page=20):
        """获取用户的历史记录（分页）"""
        skip = (page - 1) * per_page
        
        try:
            # 查询用户的历史记录
            history_cursor = self.collection.find(
                {'user_id': user_id}
            ).sort('created_at', -1).skip(skip).limit(per_page)
            
            history_list = []
            for record in history_cursor:
                history_list.append({
                    'id': str(record['_id']),
                    'image_data': record.get('image_data'),
                    'analysis_result': record.get('analysis_result'),
                    'usage_info': record.get('usage_info'),
                    'created_at': record.get('created_at').isoformat() if record.get('created_at') else None
                })
            
            # 获取总数
            total = self.collection.count_documents({'user_id': user_id})
            
            return {
                'success': True,
                'history': history_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'获取历史记录失败: {str(e)}'
            }
    
    def delete_history_item(self, user_id, history_id):
        """删除单条历史记录"""
        try:
            result = self.collection.delete_one({
                '_id': ObjectId(history_id),
                'user_id': user_id  # 确保用户只能删除自己的记录
            })
            return result.deleted_count > 0
        except Exception:
            return False
    
    def clear_user_history(self, user_id):
        """清空用户的所有历史记录"""
        try:
            result = self.collection.delete_many({'user_id': user_id})
            return {
                'success': True,
                'deleted_count': result.deleted_count
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'清空历史记录失败: {str(e)}'
            }
    
    def get_user_statistics(self, user_id):
        """获取用户统计信息"""
        try:
            # 总分析次数
            total_analyses = self.collection.count_documents({'user_id': user_id})
            
            # 最近30天的分析次数
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_analyses = self.collection.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': thirty_days_ago}
            })
            
            # 总Token使用量
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': None,
                    'total_tokens': {'$sum': '$usage_info.total_tokens'},
                    'total_prompt_tokens': {'$sum': '$usage_info.prompt_tokens'},
                    'total_completion_tokens': {'$sum': '$usage_info.completion_tokens'}
                }}
            ]
            
            token_stats = list(self.collection.aggregate(pipeline))
            
            if token_stats:
                token_usage = token_stats[0]
            else:
                token_usage = {
                    'total_tokens': 0,
                    'total_prompt_tokens': 0,
                    'total_completion_tokens': 0
                }
            
            return {
                'success': True,
                'statistics': {
                    'total_analyses': total_analyses,
                    'recent_analyses': recent_analyses,
                    'token_usage': token_usage
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'获取统计信息失败: {str(e)}'
            }
