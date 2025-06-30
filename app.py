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

        # --- 图片压缩处理 ---
        # 为了减少调用 Gemini API 的耗时与流量，这里将图片最长边压缩到 1024px，
        # 并统一保存为 JPEG(质量85)。若图片本身尺寸已足够小，则不会变更尺寸。
        try:
            img = Image.open(io.BytesIO(file_bytes))
            max_dim = 1024
            if img.width > max_dim or img.height > max_dim:
                img.thumbnail((max_dim, max_dim))

            # 转成 RGB 以避免透明通道造成文件体积过大
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            file_bytes = buf.getvalue()
        except Exception as img_err:
            print(f"图片压缩失败: {img_err}")

        # 再次检查文件大小（压缩后理论上不会超过20MB，但这里仍做保护）
        if len(file_bytes) > 20 * 1024 * 1024:  # 20MB
            return jsonify({'error': '图片文件过大，请上传小于20MB的图片'}), 400

        # 统一 MIME 类型为 JPEG
        mime_type = "image/jpeg"
        
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
                        text="""请仔细分析这张图片中的食物，并严格按照以下格式输出分析结果：

食物名称：[食物的中文名称]

热量：[具体数值] 千卡

热量等级：[低/中/高/极高]

营养成分：
碳水：[具体数值] 克
蛋白质：[具体数值] 克  
脂肪：[具体数值] 克

食用建议：[20字以内的简洁建议]

重要要求：
1. 必须给出具体的数值，不能使用"大约"、"估计"、"XX-XX"等模糊表述
2. 热量等级标准：低(<200千卡)、中(200-500千卡)、高(500-800千卡)、极高(>800千卡)
3. 营养成分数值要合理且准确，每行一个成分
4. 食用建议要简洁实用，不超过20字
5. 如果图片中没有食物，请回复"未检测到食物"

请严格按照上述格式输出，不要添加额外的解释或说明。"""
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