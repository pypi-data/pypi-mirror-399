# TBase Admin 安装和配置指南

## 📋 概述

Django TBase Admin 是一个强大的 Django 管理模块，专门用于系统性能监控和数据库优化。该模块提供了直观的 Web 界面，让管理员可以轻松查看系统状态、清理过期数据和优化数据库性能。

## 🚀 快速安装

### 1. 安装依赖

```bash
# 安装系统监控依赖
pip install psutil>=5.8.0

# 如果使用 hitcount 功能
pip install django-hitcount

# 安装 TBase Admin
pip install django-tbase-admin
```

### 2. 配置 Django 项目

在 `settings.py` 中添加以下配置：

```python
# 添加到 INSTALLED_APPS
INSTALLED_APPS = [
    # ... 其他应用
    'tbase_admin',
]

# 添加 TBase Admin 配置
TBASE_ADMIN = {
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

# 配置缓存（推荐）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tbase_admin_cache',
    }
}
```

### 3. 配置 URL

在主项目的 `urls.py` 中添加：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他 URL
    path('tbase-admin/', include('tbase_admin.urls')),
]
```

### 4. 运行迁移

```bash
python manage.py migrate
python manage.py collectstatic
```

### 5. 创建管理员用户

```bash
python manage.py createsuperuser
```

## 🔧 详细配置

### 完整配置示例

```python
TBASE_ADMIN = {
    # 默认批量大小
    'DEFAULT_BATCH_SIZE': 5000,
    
    # 默认清理天数
    'DEFAULT_CLEANUP_DAYS': 30,
    
    # 监控的表列表
    'MONITORED_TABLES': [
        'django_session',
        'hitcount_hit', 
        'hitcount_hit_count',
        'tbase_post_post',
        'tbase_page_basepage',
        'django_admin_log',
        'auth_user',
        'django_content_type',
        'django_migrations'
    ],
    
    # 警告阈值配置
    'ALERT_THRESHOLDS': {
        'SESSION_COUNT_WARNING': 10000,
        'SESSION_COUNT_CRITICAL': 50000,
        'TABLE_SIZE_WARNING_MB': 500,
        'TABLE_SIZE_CRITICAL_MB': 1000,
        'HITCOUNT_COUNT_WARNING': 100000,
        'HITCOUNT_COUNT_CRITICAL': 500000,
        'MEMORY_WARNING': 70,
        'MEMORY_CRITICAL': 85,
        'DISK_WARNING': 80,
        'DISK_CRITICAL': 90,
    },
    
    # 安全配置
    'SECURITY': {
        'require_confirmation': True,
        'max_batch_size': 10000,
        'allow_optimize_large_tables': False,
        'large_table_threshold_mb': 1000,
    }
}
```

### 日志配置

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/tbase_admin.log',
        },
    },
    'loggers': {
        'tbase_admin': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🎯 使用指南

### 访问管理界面

1. 使用管理员账号登录 Django Admin
2. 访问 `/tbase-admin/performance/` 进入性能仪表板

### 主要功能

#### 1. 系统监控
- 实时显示内存和磁盘使用情况
- 数据库连接状态监控
- 缓存状态检查

#### 2. Sessions 管理
- **快速清理**: 清理所有过期 sessions
- **高级清理**: 按天数清理，支持预览模式

#### 3. Hitcount 数据清理
- 按时间范围清理访问统计
- 支持批量处理和预览模式
- 性能优化的删除策略

#### 4. 数据库表优化
- **OPTIMIZE**: 完整优化表结构
- **ANALYZE**: 更新表统计信息
- **REPAIR**: 修复损坏的表
- **CHECK**: 检查表完整性

## 🛠️ 管理命令

### Sessions 清理

```bash
# 清理过期 sessions
python manage.py tbase_clearsessions

# 清理 7 天前的 sessions
python manage.py tbase_clearsessions --days=7

# 预览模式
python manage.py tbase_clearsessions --dry-run
```

### Hitcount 清理

```bash
# 清理 30 天前的数据
python manage.py tbase_clearhitcount --days=30

# 自定义批量大小
python manage.py tbase_clearhitcount --batch-size=10000

# 预览模式
python manage.py tbase_clearhitcount --dry-run
```

### 表优化

```bash
# 检查表状态
python manage.py tbase_optimize_tables --operation=check

# 分析表
python manage.py tbase_optimize_tables --operation=analyze

# 优化表
python manage.py tbase_optimize_tables --operation=optimize

# 指定特定表
python manage.py tbase_optimize_tables --tables django_session hitcount_hit
```

## 📊 性能优化建议

### 定期维护任务

建议设置以下定期任务：

```bash
# 每日清理过期 sessions
0 2 * * * python manage.py tbase_clearsessions

# 每周清理旧 hitcount 数据
0 3 * * 0 python manage.py tbase_clearhitcount --days=30

# 每月优化表结构
0 4 1 * * python manage.py tbase_optimize_tables --operation=analyze
```

### 监控阈值

根据系统规模调整监控阈值：

- **小型系统** (< 10,000 用户/天):
  - SESSION_COUNT_WARNING: 5,000
  - TABLE_SIZE_WARNING_MB: 100

- **中型系统** (10,000-100,000 用户/天):
  - SESSION_COUNT_WARNING: 20,000
  - TABLE_SIZE_WARNING_MB: 500

- **大型系统** (> 100,000 用户/天):
  - SESSION_COUNT_WARNING: 100,000
  - TABLE_SIZE_WARNING_MB: 2000

## 🔍 故障排除

### 常见问题

#### 1. 模块导入错误
```
ModuleNotFoundError: No module named 'psutil'
```
**解决方案**: `pip install psutil`

#### 2. 表不存在错误
```
Table 'database.hitcount_hit' doesn't exist
```
**解决方案**: 从 `MONITORED_TABLES` 中移除不存在的表，或安装相应的应用

#### 3. 权限错误
确保运行 Django 的数据库用户有以下权限：
- SELECT
- INSERT
- UPDATE
- DELETE
- CREATE
- ALTER
- INDEX
- DROP

#### 4. 内存不足
如果遇到内存不足错误：
1. 减少 `DEFAULT_BATCH_SIZE` 配置
2. 使用 `--batch-size` 参数调整批量大小
3. 在低峰期执行清理操作

### 调试模式

启用调试模式获取更多信息：

```python
LOGGING = {
    'loggers': {
        'tbase_admin': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📈 性能监控

### 关键指标

监控以下关键指标：

1. **Session 数量**: 正常应 < 10,000
2. **表大小**: 监控增长趋势
3. **内存使用**: 应 < 80%
4. **磁盘使用**: 应 < 85%
5. **清理效率**: 删除速度应 > 1000 记录/秒

### 告警设置

建议设置以下告警：

- Session 数量 > 50,000
- 单个表大小 > 1GB
- 内存使用 > 85%
- 磁盘使用 > 90%

## 🔐 安全注意事项

1. **权限控制**: 只有管理员可以访问
2. **操作确认**: 危险操作需要确认
3. **批量限制**: 限制单次操作的最大数量
4. **日志记录**: 记录所有清理和优化操作
5. **备份策略**: 执行优化前建议备份数据

## 📞 技术支持

如果遇到问题：

1. 查看日志文件 `logs/tbase_admin.log`
2. 检查 Django 管理命令输出
3. 验证数据库权限配置
4. 确认所有依赖包已正确安装

## 🔄 更新升级

升级到新版本时：

1. 备份数据库
2. 更新代码: `pip install --upgrade django-tbase-admin`
3. 运行迁移: `python manage.py migrate`
4. 收集静态文件: `python manage.py collectstatic`
5. 检查配置兼容性

---

**版本**: 1.0.0  
**更新时间**: 2024年12月  
**兼容性**: Django 3.2+, Python 3.8+