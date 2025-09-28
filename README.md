# 智能相册搜索

一个基于AI的本地照片搜索工具，支持使用自然语言或图片搜索本地照片，所有处理均在本地完成，保障隐私安全。

## 功能特性

- 自然语言搜索：输入描述文字搜索相关照片
- 以图搜图：上传图片搜索相似或相关的照片
- 本地运行：所有处理均在本地完成，不上传任何数据到云端
- 隐私安全：用户数据完全保留在本地
- 快速索引：高效处理大量照片文件

## 技术架构

- 前端：Vue 3 + TypeScript + Tailwind CSS + shadcn-vue
- 后端：Python Flask + PyTorch + CLIP + Sentence Transformers
- 索引：FAISS (Facebook AI Similarity Search)
- 桌面应用：Tauri (待集成)

## 系统要求

- macOS (本项目开发环境)
- Python 3.8+
- Node.js 16+
- 至少4GB内存 (推荐8GB或更多)
- 足够的磁盘空间存储模型文件和索引

## 快速开始

### 1. 克隆项目

```bash
# 本项目已存在 /Users/wangxt/myspace/SearchPhoto
```

### 2. 安装后端依赖

```bash
# 进入后端目录
cd /Users/wangxt/myspace/SearchPhoto/backend

# 激活虚拟环境 (如果尚未创建)
python3 -m venv venv
source venv/bin/activate

# 安装依赖包 (如果尚未安装)
pip install Flask Flask-CORS sentence-transformers transformers torch Pillow opencv-python numpy torchvision
```

### 3. 安装前端依赖

```bash
# 进入前端目录
cd /Users/wangxt/myspace/SearchPhoto/frontend

# 安装依赖
npm install
```

### 4. 启动应用

#### 方法一：使用启动脚本 (推荐)

```bash
# 在项目根目录运行
cd /Users/wangxt/myspace/SearchPhoto
./start_app.sh
```

#### 方法二：手动启动

1. 启动后端服务：

```bash
cd /Users/wangxt/myspace/SearchPhoto/backend
source venv/bin/activate
python app.py
```

2. 启动前端开发服务器：

```bash
cd /Users/wangxt/myspace/SearchPhoto/frontend
npm run dev
```

### 5. 访问应用

- 前端界面：http://localhost:3000
- 后端API：http://localhost:5000

## 使用说明

### 1. 添加照片文件夹

1. 点击"添加照片文件夹"按钮
2. 输入包含照片的文件夹路径
3. 系统将自动扫描文件夹中的照片并提取特征
4. 处理完成后，照片将被索引，可以进行搜索

### 2. 搜索照片

#### 文本搜索
1. 在搜索框输入描述文字（如"海边日落"、"家庭聚会"等）
2. 点击搜索按钮
3. 查看搜索结果

#### 以图搜图
1. 点击"以图搜图"区域的文件选择按钮
2. 选择一张图片上传
3. 系统将返回相似的图片

## 项目结构

```
/Users/wangxt/myspace/SearchPhoto/
├── frontend/                 # 前端代码
│   ├── src/                  # 源代码
│   │   ├── components/       # 组件
│   │   ├── views/            # 页面
│   │   ├── api/              # API接口
│   │   ├── stores/           # 状态管理
│   │   └── assets/           # 静态资源
│   ├── public/               # 静态资源
│   └── package.json          # 前端依赖
├── backend/                  # 后端代码
│   ├── app.py                # 主应用
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑
│   └── venv/                 # Python虚拟环境
├── docs/                     # 文档
├── assets/                   # 资源文件
├── 技术方案.md               # 技术方案文档
├── 需求背景.md               # 需求文档
├── UI设计.md                 # UI设计文档
└── start_app.sh              # 启动脚本
```

## 模型说明

本项目使用以下AI模型：
- CLIP (Contrastive Language-Image Pretraining)：用于将图像和文本映射到同一特征空间
- Sentence Transformers：用于文本编码
- FAISS：用于高效相似度搜索

## 性能优化

- 使用FAISS进行快速向量相似度搜索
- 所有AI推理在本地完成
- 图像特征提取后缓存到本地
- 支持批量处理

## 数据安全

- 所有数据处理均在本地完成
- 不上传任何用户数据到云端
- 图像特征存储在本地
- 支持删除索引和数据清理

## 扩展功能

- [ ] 按时间轴查看照片
- [ ] 地理位置聚类
- [ ] 人物识别与聚类
- [ ] 自动标签生成
- [ ] 照片推荐
- [ ] 打包为桌面应用 (Tauri)

## 开发

### 前端开发

```bash
cd /Users/wangxt/myspace/SearchPhoto/frontend
npm run dev        # 开发模式
npm run build      # 构建生产版本
```

### 后端开发

```bash
cd /Users/wangxt/myspace/SearchPhoto/backend
source venv/bin/activate
python app.py      # 启动后端服务
```

## 故障排除

### 后端问题

1. 模型下载慢或失败
   - 检查网络连接
   - 验证transformers和torch版本兼容性

2. 内存不足
   - 减少批量处理大小
   - 增加系统交换空间

### 前端问题

1. API连接失败
   - 确认后端服务在运行 (http://localhost:5000)
   - 检查CORS设置

2. 组件样式异常
   - 运行 `npm install` 重新安装依赖
   - 检查Tailwind CSS配置

## 许可证

[请在此处添加许可证信息]