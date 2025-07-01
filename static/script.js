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

    // 用户认证相关
    const logoutBtn = document.getElementById('logoutBtn');

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

    // 退出登录按钮点击
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    // 初始化历史记录
    loadHistoryFromServer();

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

            // 检查是否是认证错误
            if (String(error).includes('HTTP 401')) {
                showError('登录已过期，请重新登录');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
                return;
            }

            // 根据错误信息判断是否是网关或网络错误
            if (String(error).includes('HTTP 502')) {
                showError('服务器超时或暂不可用，请稍后再试');
            } else if (String(error).includes('HTTP 403')) {
                showError('权限不足，请联系管理员');
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
        const formattedResult = formatAnalysisResult(analysis);
        resultContent.innerHTML = formattedResult;

        // 隐藏或移除token使用信息显示
        if (typeof usageInfo !== 'undefined') {
            const infoEl = document.getElementById('usageInfo');
            if (infoEl) infoEl.style.display = 'none';
        }

        resultCard.style.display = 'block';
        errorCard.style.display = 'none';

        saveToServer(analysis, usage);

        // 更新热量仪表盘
        if (typeof onAnalysisComplete === 'function') {
            onAnalysisComplete(analysis);
        }

        resultCard.scrollIntoView({ behavior: 'smooth' });
    }

    function formatAnalysisResult(analysis) {
        // 解析AI返回的结构化数据
        const lines = analysis.split('\n').filter(line => line.trim());
        let foodName = '';
        let calories = '';
        let calorieLevel = '';
        let weight = '';
        let carb = '';
        let protein = '';
        let fat = '';
        let suggestion = '';

        lines.forEach(line => {
            const trimmedLine = line.trim();
            if (trimmedLine.startsWith('食物名称：')) {
                foodName = trimmedLine.replace('食物名称：', '').trim();
            } else if (trimmedLine.startsWith('热量：')) {
                calories = trimmedLine.replace('热量：', '').trim();
            } else if (trimmedLine.startsWith('热量等级：')) {
                calorieLevel = trimmedLine.replace('热量等级：', '').trim();
            } else if (trimmedLine.startsWith('重量：')) {
                weight = trimmedLine.replace('重量：', '').trim();
            } else if (trimmedLine.startsWith('碳水：')) {
                carb = trimmedLine.replace('碳水：', '').trim();
            } else if (trimmedLine.startsWith('蛋白质：')) {
                protein = trimmedLine.replace('蛋白质：', '').trim();
            } else if (trimmedLine.startsWith('脂肪：')) {
                fat = trimmedLine.replace('脂肪：', '').trim();
            } else if (trimmedLine.startsWith('食用建议：')) {
                suggestion = trimmedLine.replace('食用建议：', '').trim();
            }
        });

        // 如果解析失败，尝试更灵活的解析
        if (!foodName && !calories) {
            // 尝试更宽松的匹配
            lines.forEach(line => {
                const trimmedLine = line.trim();
                if (trimmedLine.includes('食物') && trimmedLine.includes('：')) {
                    foodName = trimmedLine.split('：')[1]?.trim() || '';
                } else if (trimmedLine.includes('热量') && trimmedLine.includes('：')) {
                    calories = trimmedLine.split('：')[1]?.trim() || '';
                } else if (trimmedLine.includes('等级') && trimmedLine.includes('：')) {
                    calorieLevel = trimmedLine.split('：')[1]?.trim() || '';
                }
            });
        }

        // 如果还是解析失败，返回简化的原始文本
        if (!foodName && !calories) {
            return `<div class="compact-result"><pre style="margin: 0; font-size: 14px; line-height: 1.5;">${analysis}</pre></div>`;
        }

        // 提取数字
        const calorieNum = calories.replace(/[^\d]/g, '') || '0';
        const levelBadgeClass = getLevelBadgeClass(calorieLevel);
        
        return `
            <div class="pc-analysis-result">
                <div class="result-row">
                    <div class="food-info">
                        <h3 class="food-name">${foodName}</h3>
                        ${weight ? `<span class="food-weight">${weight}</span>` : ''}
                    </div>
                    
                    <div class="calorie-info">
                        <span class="calorie-number">${calorieNum}</span>
                        <span class="calorie-unit">千卡</span>
                        <span class="calorie-badge ${levelBadgeClass}">${calorieLevel}</span>
                    </div>
                    
                    <div class="nutrition-inline">
                        <div class="nutrition-item">
                            <span class="nutrition-dot carb"></span>
                            <span class="nutrition-text">碳水 <strong>${carb}</strong></span>
                        </div>
                        <div class="nutrition-item">
                            <span class="nutrition-dot protein"></span>
                            <span class="nutrition-text">蛋白质 <strong>${protein}</strong></span>
                        </div>
                        <div class="nutrition-item">
                            <span class="nutrition-dot fat"></span>
                            <span class="nutrition-text">脂肪 <strong>${fat}</strong></span>
                        </div>
                    </div>
                    
                    ${suggestion ? `<div class="suggestion-inline">
                        <span class="suggestion-icon">💡</span>
                        <span class="suggestion-text">${suggestion}</span>
                    </div>` : ''}
                </div>
            </div>
        `;
    }

    function getLevelBadgeClass(level) {
        switch(level) {
            case '低': return 'level-low';
            case '中': return 'level-medium';
            case '高': return 'level-high';
            case '极高': return 'level-extreme';
            default: return 'level-medium';
        }
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

    // 用户认证相关函数
    function logout() {
        if (confirm('确定要退出登录吗？')) {
            fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/auth/login';
                } else {
                    alert('退出登录失败');
                }
            })
            .catch(error => {
                console.error('退出登录错误:', error);
                alert('退出登录失败');
            });
        }
    }

    // 保存到服务器
    function saveToServer(analysis, usage) {
        if (!selectedFile) return;

        const data = {
            image_data: previewImg.src,
            analysis_result: analysis,
            usage_info: usage
        };

        fetch('/api/history/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('历史记录保存成功');
                loadHistoryFromServer();
            } else {
                console.error('保存历史记录失败:', data.error);
            }
        })
        .catch(error => {
            console.error('保存历史记录错误:', error);
        });
    }

    // 从服务器加载历史记录
    function loadHistoryFromServer() {
        fetch('/api/history/')
        .then(response => {
            if (response.status === 401) {
                // 认证失败，重定向到登录页
                window.location.href = '/auth/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                displayHistory(data.history);
            } else if (data) {
                console.error('加载历史记录失败:', data.error);
                historyEmpty.style.display = 'block';
                historyList.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('加载历史记录错误:', error);
            historyEmpty.style.display = 'block';
            historyList.style.display = 'none';
        });
    }

    function displayHistory(history) {
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

        // 格式化日期
        const date = item.created_at ? new Date(item.created_at).toLocaleString('zh-CN') : '未知时间';

        li.innerHTML = `
            <div class="history-item-header">
                <span class="history-date">${date}</span>
                <button class="history-delete" onclick="deleteHistoryItemFromServer('${item.id}')">删除</button>
            </div>
            <div class="history-image-container">
                <img src="${item.image_data}" alt="历史图片" class="history-image" onclick="showImageModal('${item.image_data}')">
            </div>
            <div class="history-result">${item.analysis_result}</div>
            <div class="history-usage">Token: ${item.usage_info.total_tokens} (输入: ${item.usage_info.prompt_tokens}, 输出: ${item.usage_info.completion_tokens})</div>
        `;
        return li;
    }

    function toggleHistory() {
        historyVisible = !historyVisible;
        if (historyVisible) {
            historyCard.style.display = 'block';
            // 打开侧边栏
            historyCard.classList.add('open');
            document.body.classList.add('history-open');
            historyToggleBtn.innerHTML = '<span>📝</span>隐藏记录';
            loadHistory();
        } else {
            historyCard.classList.remove('open');
            document.body.classList.remove('history-open');
            historyCard.style.display = 'block';  // 维持block，靠transform隐藏
            historyToggleBtn.innerHTML = '<span>📝</span>历史记录';
        }
    }

    function clearAllHistory() {
        if (confirm('确定要清空所有历史记录吗？此操作不可撤销。')) {
            fetch('/api/history/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadHistoryFromServer();
                    alert('历史记录已清空');
                } else {
                    alert('清空失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('清空历史记录错误:', error);
                alert('清空失败');
            });
        }
    }

    // 全局函数，供HTML调用
    window.deleteHistoryItemFromServer = function(id) {
        if (confirm('确定要删除这条记录吗？')) {
            fetch(`/api/history/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadHistoryFromServer();
                } else {
                    alert('删除失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('删除历史记录错误:', error);
                alert('删除失败');
            });
        }
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

    // ===== 热量仪表盘功能 =====
    const calorieDashboard = document.getElementById('calorieDashboard');
    const currentCaloriesEl = document.getElementById('currentCalories');
    const targetCaloriesEl = document.getElementById('targetCalories');
    const remainingCaloriesEl = document.getElementById('remainingCalories');
    const calorieProgressEl = document.getElementById('calorieProgress');
    const dashboardDateEl = document.getElementById('dashboardDate');
    const circleProgress = document.querySelector('.circle-progress');

    let dailyCalorieGoal = 2000;
    let currentCalories = 0;

    // 初始化热量仪表盘
    function initCalorieDashboard() {
        // 设置当前日期
        const today = new Date();
        const dateStr = today.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        if (dashboardDateEl) {
            dashboardDateEl.textContent = dateStr;
        }

        // 获取用户热量目标
        loadCalorieGoal();

        // 加载今日热量摄入（从历史记录计算）
        loadTodayCalories();
    }

    // 获取用户热量目标
    function loadCalorieGoal() {
        fetch('/api/user/calorie-goal')
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    dailyCalorieGoal = result.daily_calorie_goal || 2000;
                    updateCalorieDashboard();
                }
            })
            .catch(error => {
                console.error('Error loading calorie goal:', error);
                // 使用默认值
                updateCalorieDashboard();
            });
    }

    // 加载今日热量摄入
    function loadTodayCalories() {
        fetch('/api/history/')
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    currentCalories = calculateTodayCalories(result.history);
                    updateCalorieDashboard();
                }
            })
            .catch(error => {
                console.error('Error loading today calories:', error);
            });
    }

    // 从历史记录计算今日热量
    function calculateTodayCalories(history) {
        const today = new Date().toDateString();
        let totalCalories = 0;

        history.forEach(record => {
            const recordDate = new Date(record.created_at).toDateString();
            if (recordDate === today) {
                // 从分析结果中提取热量信息
                const calories = extractCaloriesFromAnalysis(record.analysis_result);
                if (calories) {
                    totalCalories += calories;
                }
            }
        });

        return totalCalories;
    }

    // 从分析结果中提取热量数值
    function extractCaloriesFromAnalysis(analysisText) {
        if (!analysisText) return 0;

        // 匹配热量信息，格式如："热量：XXX 千卡"
        const calorieMatch = analysisText.match(/热量[：:]\s*(\d+(?:\.\d+)?)\s*千卡/);
        if (calorieMatch) {
            return parseFloat(calorieMatch[1]);
        }

        return 0;
    }

    // 更新热量仪表盘显示
    function updateCalorieDashboard() {
        if (!calorieDashboard) return;

        const remaining = Math.max(0, dailyCalorieGoal - currentCalories);
        const progress = Math.min(100, (currentCalories / dailyCalorieGoal) * 100);

        // 更新数值显示
        if (currentCaloriesEl) {
            currentCaloriesEl.textContent = Math.round(currentCalories);
        }
        if (targetCaloriesEl) {
            targetCaloriesEl.textContent = dailyCalorieGoal + ' kcal';
        }
        if (remainingCaloriesEl) {
            remainingCaloriesEl.textContent = Math.round(remaining) + ' kcal';
        }
        if (calorieProgressEl) {
            calorieProgressEl.textContent = Math.round(progress) + '%';
        }

        // 更新圆形进度条
        if (circleProgress) {
            const circumference = 2 * Math.PI * 80; // r = 80
            const offset = circumference - (progress / 100) * circumference;
            circleProgress.style.strokeDashoffset = offset;

            // 根据进度改变颜色
            if (progress >= 100) {
                circleProgress.style.stroke = '#ef4444'; // 红色：超标
            } else if (progress >= 80) {
                circleProgress.style.stroke = '#f59e0b'; // 黄色：接近目标
            } else {
                circleProgress.style.stroke = 'white'; // 白色：正常
            }
        }
    }

    // 监听分析完成事件，更新热量数据
    function onAnalysisComplete(analysisResult) {
        const calories = extractCaloriesFromAnalysis(analysisResult);
        if (calories > 0) {
            currentCalories += calories;
            updateCalorieDashboard();

            // 添加动画效果
            if (currentCaloriesEl) {
                currentCaloriesEl.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    currentCaloriesEl.style.transform = 'scale(1)';
                }, 200);
            }
        }
    }

    // 将onAnalysisComplete函数暴露到全局作用域
    window.onAnalysisComplete = onAnalysisComplete;

    // 初始化仪表盘
    if (calorieDashboard) {
        initCalorieDashboard();
    }
});