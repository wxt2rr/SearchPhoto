# 智能相册搜索

一个基于AI的本地照片搜索工具，支持使用自然语言或图片搜索本地照片，所有处理均在本地完成，保障隐私安全。

## 功能特性

- 自然语言搜索：输入描述文字搜索相关照片
- 以图搜图：上传图片搜索相似或相关的照片
- 文件夹管理：添加、刷新和删除照片文件夹索引
- 本地运行：所有处理均在本地完成，不上传任何数据到云端
- 隐私安全：用户数据完全保留在本地，支持数据清除功能
- 快速索引：高效处理大量照片文件
- 搜索历史：记录和管理搜索历史
- 图片预览：支持网格、列表等多种视图模式

## 技术架构

- 前端：Vue 3 + TypeScript + Vite + Tailwind CSS + shadcn-vue + Pinia
- 后端：Python Flask + PyTorch + CLIP + Sentence Transformers
- 索引：FAISS (Facebook AI Similarity Search) + SQLite
- 数据存储：IndexedDB + 本地文件系统
- 桌面应用：Tauri (计划集成)

## 系统要求

- 操作系统：macOS、Linux 或 Windows
- Python 3.8+
- Node.js 16+ / npm 8+
- 至少4GB内存 (推荐8GB或更多用于AI模型处理)
- 足够的磁盘空间存储AI模型文件和照片索引数据
- 现代浏览器（支持ES6+、IndexedDB、Web Workers）

## 快速开始

### 1. 环境准备

1. 确保已安装Python 3.8+和Node.js 16+
2. 克隆项目仓库到本地

```bash
# 本项目已存在 /Users/wangxt/myspace/SearchPhoto
```

### 2. 安装后端依赖

```bash
# 进入后端目录
cd /Users/wangxt/myspace/SearchPhoto/backend

# 激活虚拟环境 (如果尚未创建)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
# venv\Scripts\activate   # Windows

# 安装依赖包 (如果尚未安装)
pip install -r requirements.txt
# 或单独安装
pip install Flask Flask-CORS sentence-transformers transformers torch Pillow opencv-python numpy torchvision faiss-cpu
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
- 应用启动后，按照界面引导添加照片文件夹并开始搜索

## 使用说明

### 1. 初始化设置

1. 启动应用后，点击"添加照片文件夹"按钮
2. 选择包含照片的本地文件夹
3. 系统将自动扫描文件夹中的照片并建立索引
4. 查看处理进度，等待索引完成

### 2. 搜索功能

#### 文本搜索
1. 在搜索框输入描述文字（如"海边日落"、"家庭聚会"、"猫咪玩耍"等）
2. 查看智能提示和搜索建议
3. 点击搜索按钮或按回车键查看结果

#### 以图搜图
1. 点击"以图搜图"区域或拖拽图片到指定区域
2. 选择一张图片上传
3. 系统将返回相似的图片

### 3. 文件夹管理

1. 在"我的文件夹"中查看已处理的文件夹列表
2. 查看每个文件夹的处理状态和最后更新时间
3. 支持刷新单个文件夹的索引
4. 可删除不再需要的文件夹索引

### 4. 结果展示与操作

- 选择网格、列表等不同视图模式查看结果
- 鼠标悬停查看图片详细信息（时间、地点等）
- 支持收藏、标签、分享等快捷操作
- 支持批量选择和操作多张图片
- 使用筛选器按时间、地点等条件进一步筛选

## 项目结构

```
/Users/wangxt/myspace/SearchPhoto/
├── frontend/                 # 前端代码
│   ├── src/                  # 源代码
│   │   ├── components/       # 可复用UI组件
│   │   │   ├── FileProcessor/ # 文件处理相关组件
│   │   │   ├── ImageGrid/     # 图片网格展示组件
│   │   │   ├── SearchBar/     # 搜索框组件
│   │   │   └── ...
│   │   ├── views/            # 页面组件
│   │   │   ├── Home.vue      # 主页面
│   │   │   ├── Search.vue    # 搜索结果页面
│   │   │   └── ...
│   │   ├── composables/      # Vue 3 Composables
│   │   │   ├── useImageProcessor/ # 图片处理逻辑
│   │   │   ├── useSearch/    # 搜索逻辑
│   │   │   └── ...
│   │   ├── api/              # API接口封装
│   │   │   ├── imageApi.ts   # 图像处理API
│   │   │   ├── searchApi.ts  # 搜索API
│   │   │   └── index.ts      # API入口
│   │   ├── stores/           # Pinia状态管理
│   │   │   ├── imageStore.ts # 图片数据存储
│   │   │   ├── searchStore.ts # 搜索历史和设置
│   │   │   └── ...
│   │   ├── assets/           # 静态资源
│   │   ├── utils/            # 工具函数
│   │   └── types/            # TypeScript类型定义
│   ├── public/               # 静态资源
│   ├── package.json          # 前端依赖
│   └── vite.config.ts        # 构建配置
├── backend/                  # 后端代码
│   ├── app.py                # 主应用
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑
│   │   ├── image_processing.py # 图像处理服务
│   │   ├── semantic_search.py  # 语义搜索服务
│   │   └── index_management.py # 索引管理服务
│   ├── venv/                 # Python虚拟环境
│   └── requirements.txt      # Python依赖
├── docs/                     # 文档
├── assets/                   # 资源文件
├── 技术方案.md               # 技术方案文档
├── 需求背景.md               # 需求文档
├── UI设计.md                 # UI设计文档
├── README.md                 # 项目说明
├── start_app.sh              # 启动脚本
└── .gitignore                # Git忽略文件
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
