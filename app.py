from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import base64
from PIL import Image
import io

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB 最大文件大小

# 初始化Gemini客户端
client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY'),
    http_options={"base_url": os.getenv('GEMINI_BASE_URL')},
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_calories():
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '请选择要上传的图片'}), 400
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in allowed_extensions:
            return jsonify({'error': '不支持的图片格式，请上传 PNG、JPG、JPEG、GIF、BMP 或 WEBP 格式的图片'}), 400
        
        # 读取图片数据
        file_bytes = file.read()
        
        # 检查文件大小
        if len(file_bytes) > 20 * 1024 * 1024:  # 20MB
            return jsonify({'error': '图片文件过大，请上传小于20MB的图片'}), 400
        
        # 获取MIME类型
        mime_type = f"image/{file_extension}" if file_extension != 'jpg' else "image/jpeg"
        
        # 调用Gemini API进行分析
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=types.Content(
                parts=[
                    types.Part(
                        inline_data=types.Blob(
                            data=file_bytes,
                            mime_type=mime_type
                        )
                    ),
                    types.Part(
                        text="""请仔细分析这张图片中的食物，并提供详细的卡路里分析。请按照以下要求回答：

1. 识别图片中的所有食物种类和估算的分量
2. 计算每种食物的大概卡路里含量
3. 提供总卡路里数
4. 给出主要营养成分分析（蛋白质、脂肪、碳水化合物）
5. 如果可能，提供一些健康建议

请用中文回答，格式要清晰易读。如果图片中没有食物，请说明情况。"""
                    )
                ]
            )
        )
        
        # 获取分析结果
        analysis_result = response.text
        
        # 获取token使用情况
        usage_info = {
            'prompt_tokens': response.usage_metadata.prompt_token_count,
            'completion_tokens': response.usage_metadata.candidates_token_count,
            'total_tokens': response.usage_metadata.total_token_count
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'usage': usage_info
        })
        
    except Exception as e:
        print(f"分析错误: {str(e)}")
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件过大，请上传小于20MB的图片'}), 413

if __name__ == '__main__':
    # 检查环境变量
    if not os.getenv('GEMINI_API_KEY'):
        print("错误: 请设置 GEMINI_API_KEY 环境变量")
        exit(1)
    if not os.getenv('GEMINI_BASE_URL'):
        print("错误: 请设置 GEMINI_BASE_URL 环境变量")
        exit(1)
    
    # 根据部署环境动态选择端口，优先 PORT，其次 WEB_PORT，默认 5000
    run_port = int(os.getenv('PORT') or os.getenv('WEB_PORT') or "5000")
    app.run(host='0.0.0.0', port=run_port) 