# Django TBase Admin

[![PyPI version](https://badge.fury.io/py/django-tbase-admin.svg)](https://badge.fury.io/py/django-tbase-admin)
[![Python versions](https://img.shields.io/pypi/pyversions/django-tbase-admin.svg)](https://pypi.org/project/django-tbase-admin/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Django versions](https://img.shields.io/pypi/frameworkversions/django-tbase-admin.svg)](https://pypi.org/project/django-tbase-admin/)

Django TBase Admin 是一个强大的 Django 管理模块，专门用于系统性能监控和数据库优化。该模块提供了直观的 Web 界面，让管理员可以轻松查看系统状态、清理过期数据和优化数据库性能。

## ✨ 主要功能

### 📊 性能监控仪表板
- 实时显示数据库表统计信息
- 监控表大小和记录数量
- 提供可视化性能指标
- 自动刷新和状态指示器

### 🧹 Session 管理
- 查看当前活跃 sessions 数量
- 清理过期 sessions
- 释放数据库空间
- 批量处理支持

### 📈 Hitcount 数据管理
- 统计访问记录数据
- 按时间范围清理历史数据
- 支持批量操作和预览模式
- 性能优化的删除策略

### ⚡ 数据库优化
- 表优化操作
- 索引重建
- 查询性能分析
- 智能表选择

## 🚀 快速开始

### 安装

使用 pip 安装：

```bash
pip install django-tbase-admin
```

### 配置

1. 在 `settings.py` 中添加模块：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'tbase_admin',
]
```

2. 在主项目的 `urls.py` 中包含模块路由：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他 URL
    path('tbase-admin/', include('tbase_admin.urls')),
]
```

3. 运行数据库迁移：

```bash
python manage.py migrate
```

4. 收集静态文件：

```bash
python manage.py collectstatic
```

### 访问

使用管理员账号登录 Django Admin，然后访问 `/tbase-admin/performance/` 进入性能仪表板。

## 📖 详细文档

### 核心功能

#### 性能仪表板

访问路径：`/tbase-admin/performance/`

仪表板显示以下信息：
- **数据库表统计**：各表的行数和占用空间
- **实时数据刷新**：点击刷新按钮获取最新数据
- **可视化图表**：表大小和行数的直观展示

#### Sessions 清理

**功能**：清理过期的用户会话数据

**操作步骤**：
1. 在性能仪表板找到 "Sessions 管理" 区域
2. 点击 "清理 Sessions" 按钮
3. 系统会自动清理过期会话并显示删除的记录数

#### Hitcount 数据清理

**功能**：清理网站的访问统计数据

**参数设置**：
- **保留天数**：删除多少天前的数据（默认 30 天）
- **批量大小**：每次处理的数据量（默认 5000）
- **预览模式**：显示将要删除的数据量，不实际删除

#### 数据库表优化

**功能**：优化数据库表结构，提高查询性能

**操作步骤**：
1. 在仪表板找到 "表优化" 区域
2. 选择要优化的表（可多选）
3. 点击 "优化选中表" 按钮
4. 等待优化完成

### 管理命令

模块提供了以下管理命令：

```bash
# 清理过期 sessions
python manage.py tbase_clearsessions

# 清理 hitcount 数据
python manage.py tbase_clearhitcount --days=30 --batch-size=5000

# 预览模式清理
python manage.py tbase_clearhitcount --dry-run
```

### API 接口

模块提供 RESTful API 用于集成：

```http
GET  /tbase-admin/api/stats/     # 获取数据库统计
POST /tbase-admin/cleanup/sessions/  # 清理 sessions
POST /tbase-admin/cleanup/hitcount/  # 清理 hitcount
POST /tbase-admin/optimize/tables/   # 优化表
```

## ⚙️ 配置选项

可以在 `settings.py` 中添加自定义配置：

```python
TBASE_ADMIN = {
    'DEFAULT_BATCH_SIZE': 5000,
    'DEFAULT_CLEANUP_DAYS': 30,
    'MONITORED_TABLES': [
        'django_session',
        'hitcount_hit',
        'hitcount_hit_count',
        'tbase_post_post',
        'tbase_page_basepage',
        'django_admin_log'
    ],
    'ALERT_THRESHOLDS': {
        'SESSION_COUNT_WARNING': 10000,
        'TABLE_SIZE_WARNING_MB': 500,
        'HITCOUNT_COUNT_WARNING': 100000,
    }
}
```

## 🔧 开发

### 开发环境设置

1. 克隆仓库：
```bash
git clone https://github.com/terrychan/django-tbase-admin.git
cd django-tbase-admin
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

4. 运行测试：
```bash
pytest
```

### 代码质量

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码风格检查
- **MyPy**: 类型检查

```bash
black tbase_admin/
flake8 tbase_admin/
mypy tbase_admin/
```

## 📋 系统要求

- Python 3.8+
- Django 3.2+
- MySQL 5.7+ 或 PostgreSQL 10+ (推荐)

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 GPL-3.0 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 感谢 Django 社区的优秀框架
- 感谢所有贡献者的支持

## 📞 支持

如果遇到问题或需要帮助：

1. 查看 [文档](https://django-tbase-admin.readthedocs.io/)
2. 搜索 [Issues](https://github.com/terrychan/django-tbase-admin/issues)
3. 创建新的 Issue

---

**注意**: 这是一个开源项目，欢迎社区贡献和反馈！