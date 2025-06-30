document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImage = document.getElementById('removeImage');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultCard = document.getElementById('resultCard');
    const resultContent = document.getElementById('resultContent');
    const usageInfo = document.getElementById('usageInfo');
    const errorCard = document.getElementById('errorCard');
    const errorMessage = document.getElementById('errorMessage');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loadingSpinner = analyzeBtn.querySelector('.loading-spinner');

    // 历史记录相关元素
    const historyToggleBtn = document.getElementById('historyToggleBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const historyCard = document.getElementById('historyCard');
    const historyEmpty = document.getElementById('historyEmpty');
    const historyList = document.getElementById('historyList');

    let selectedFile = null;
    let historyVisible = false;
    const HISTORY_KEY = 'calorie_analyzer_history';

    // 点击上传区域
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    // 文件选择
    imageInput.addEventListener('change', handleFileSelect);

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // 移除图片
    removeImage.addEventListener('click', () => {
        selectedFile = null;
        imagePreview.style.display = 'none';
        uploadArea.style.display = 'block';
        analyzeBtn.disabled = true;
        hideResults();
        imageInput.value = '';
    });

    // 分析按钮
    analyzeBtn.addEventListener('click', analyzeImage);

    // 历史记录按钮
    historyToggleBtn.addEventListener('click', toggleHistory);
    clearHistoryBtn.addEventListener('click', clearAllHistory);

    // 初始化历史记录
    loadHistory();

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    }

    function handleFile(file) {
        // 检查文件类型
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            showError('不支持的图片格式，请上传 PNG、JPG、JPEG、GIF、BMP 或 WEBP 格式的图片');
            return;
        }

        // 检查文件大小 (20MB)
        if (file.size > 20 * 1024 * 1024) {
            showError('图片文件过大，请上传小于20MB的图片');
            return;
        }

        selectedFile = file;
        showImagePreview(file);
        analyzeBtn.disabled = false;
        hideResults();
    }

    function showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadArea.style.display = 'none';
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    function analyzeImage() {
        if (!selectedFile) {
            showError('请先选择要分析的图片');
            return;
        }

        // 显示加载状态
        setLoading(true);
        hideResults();

        const formData = new FormData();
        formData.append('image', selectedFile);

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(async response => {
            // 如果服务器返回非 2xx 状态，尝试读取文本并抛出错误
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            return response.json();
        })
        .then(data => {
            setLoading(false);
            if (data.success) {
                showResult(data.analysis, data.usage);
            } else {
                showError(data.error || '分析失败，请重试');
            }
        })
        .catch(error => {
            setLoading(false);
            console.error('Error:', error);
            // 根据错误信息判断是否是网关或网络错误
            if (String(error).includes('HTTP 502')) {
                showError('服务器超时或暂不可用，请稍后再试');
            } else {
                showError('网络错误，请检查网络连接后重试');
            }
        });
    }

    function setLoading(loading) {
        if (loading) {
            btnText.textContent = '分析中...';
            loadingSpinner.style.display = 'block';
            analyzeBtn.disabled = true;
        } else {
            btnText.textContent = '开始分析';
            loadingSpinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    }

    function showResult(analysis, usage) {
        resultContent.textContent = analysis;
        
        // 显示token使用情况
        usageInfo.innerHTML = `
            <strong>Token使用情况:</strong> 
            输入: ${usage.prompt_tokens} | 
            输出: ${usage.completion_tokens} | 
            总计: ${usage.total_tokens}
        `;
        
        resultCard.style.display = 'block';
        errorCard.style.display = 'none';
        
        // 保存到历史记录
        saveToHistory(analysis, usage);
        
        // 平滑滚动到结果区域
        resultCard.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorCard.style.display = 'block';
        resultCard.style.display = 'none';
        
        // 平滑滚动到错误区域
        errorCard.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        resultCard.style.display = 'none';
        errorCard.style.display = 'none';
    }

    function saveToHistory(analysis, usage) {
        if (!selectedFile) return;

        const historyItem = {
            id: Date.now(),
            date: new Date().toLocaleString('zh-CN'),
            imageData: previewImg.src,
            analysis: analysis,
            usage: usage
        };

        const history = getHistory();
        history.unshift(historyItem);

        // 只保留最近50条记录
        if (history.length > 50) {
            history.splice(50);
        }

        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        loadHistory();
    }

    function getHistory() {
        try {
            const history = localStorage.getItem(HISTORY_KEY);
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Failed to load history:', error);
            return [];
        }
    }

    function loadHistory() {
        const history = getHistory();
        
        if (history.length === 0) {
            historyEmpty.style.display = 'block';
            historyList.style.display = 'none';
            return;
        }

        historyEmpty.style.display = 'none';
        historyList.style.display = 'block';
        historyList.innerHTML = '';

        history.forEach(item => {
            const historyItemElement = createHistoryItemElement(item);
            historyList.appendChild(historyItemElement);
        });
    }

    function createHistoryItemElement(item) {
        const li = document.createElement('li');
        li.className = 'history-item';
        li.innerHTML = `
            <div class="history-item-header">
                <span class="history-date">${item.date}</span>
                <button class="history-delete" onclick="deleteHistoryItem(${item.id})">删除</button>
            </div>
            <div class="history-image-container">
                <img src="${item.imageData}" alt="历史图片" class="history-image" onclick="showImageModal('${item.imageData}')">
            </div>
            <div class="history-result">${item.analysis}</div>
            <div class="history-usage">Token: ${item.usage.total_tokens} (输入: ${item.usage.prompt_tokens}, 输出: ${item.usage.completion_tokens})</div>
        `;
        return li;
    }

    function toggleHistory() {
        historyVisible = !historyVisible;
        if (historyVisible) {
            historyCard.style.display = 'block';
            historyToggleBtn.innerHTML = '<span>📝</span>隐藏记录';
            loadHistory();
        } else {
            historyCard.style.display = 'none';
            historyToggleBtn.innerHTML = '<span>📝</span>历史记录';
        }
    }

    function clearAllHistory() {
        if (confirm('确定要清空所有历史记录吗？此操作不可撤销。')) {
            localStorage.removeItem(HISTORY_KEY);
            loadHistory();
        }
    }

    // 全局函数，供HTML调用
    window.deleteHistoryItem = function(id) {
        const history = getHistory();
        const filteredHistory = history.filter(item => item.id !== id);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(filteredHistory));
        loadHistory();
    };

    window.showImageModal = function(imageSrc) {
        // 创建模态框显示大图
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            cursor: pointer;
        `;
        
        const img = document.createElement('img');
        img.src = imageSrc;
        img.style.cssText = `
            max-width: 90%;
            max-height: 90%;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        `;
        
        modal.appendChild(img);
        document.body.appendChild(modal);
        
        modal.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    };
}); 