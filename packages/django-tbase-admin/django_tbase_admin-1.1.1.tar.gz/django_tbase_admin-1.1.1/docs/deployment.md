# Tbase_Admin 模块部署文档

## 概述

Tbase_Admin 是一个 Django 管理模块，提供性能监控、数据库优化和系统维护功能。该模块基于 Django Admin 框架构建，集成了数据库统计、缓存清理和表优化等功能。

## 功能特性

- 性能监控仪表板
- 数据库统计信息展示
- Session 清理功能
- Hitcount 数据清理
- 数据库表优化
- 自定义 Admin 界面

## 系统要求

- Python 3.8+
- Django 4.0+
- MySQL 5.7+ 或 PostgreSQL 10+
- Redis (可选，用于缓存)

## 安装步骤

### 1. 模块配置

在 `settings.py` 中添加模块：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'tbase_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

### 2. URL 配置

在主项目的 `urls.py` 中包含模块路由：

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tbase-admin/', include('tbase_admin.urls')),
    # ... 其他路由
]
```

### 3. 数据库迁移

```bash
python manage.py makemigrations tbase_admin
python manage.py migrate
```

### 4. 静态文件收集

```bash
python manage.py collectstatic
```

### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

## 配置说明

### 管理命令

模块提供了以下管理命令：

- `clearsessions`: 清理过期 sessions
- `clearhitcount`: 清理 hitcount 数据

### 权限配置

所有功能都需要 `staff_member_required` 权限，确保只有管理员可以访问。

### 自定义配置

可以在 `settings.py` 中添加以下配置：

```python
# 性能监控配置
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
    ]
}
```

## 部署注意事项

### 1. 生产环境配置

确保在生产环境中：

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
```

### 2. 数据库权限

确保数据库用户具有以下权限：

- SELECT
- INSERT
- UPDATE
- DELETE
- OPTIMIZE
- INDEX

### 3. 日志配置

配置日志记录：

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/tbase_admin.log',
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

### 4. 定时任务

建议设置定时任务进行自动清理：

```bash
# 每天凌晨清理 sessions
0 2 * * * /path/to/venv/bin/python /path/to/manage.py clearsessions

# 每周清理 hitcount 数据
0 3 * * 0 /path/to/venv/bin/python /path/to/manage.py clearhitcount
```

## 性能优化

### 1. 数据库索引

确保以下字段有索引：

- `django_session.session_key`
- `hitcount_hit.created`
- `django_admin_log.action_time`

### 2. 缓存配置

配置 Redis 缓存：

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. 连接池配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,
    }
}
```

## 监控和告警

### 1. 健康检查

设置健康检查端点：

```python
# urls.py
from tbase_admin.views import get_database_stats

urlpatterns = [
    path('health/', get_database_stats, name='health_check'),
]
```

### 2. 告警配置

配置告警阈值：

```python
TBASE_ADMIN_ALERTS = {
    'SESSION_COUNT_WARNING': 10000,
    'TABLE_SIZE_WARNING_MB': 500,
    'HITCOUNT_COUNT_WARNING': 100000,
}
```

## 故障排除

### 常见问题

1. **权限错误**: 确保用户具有 staff 权限
2. **数据库连接失败**: 检查数据库配置和权限
3. **静态文件缺失**: 运行 `collectstatic` 命令
4. **模板渲染错误**: 检查模板文件路径和语法

### 调试模式

启用调试模式：

```python
# settings.py
DEBUG = True
LOGGING_LEVEL = 'DEBUG'
```

### 日志分析

查看错误日志：

```bash
tail -f /var/log/django/tbase_admin.log
```

## 安全考虑

1. **访问控制**: 确保只有授权用户可以访问
2. **SQL 注入**: 使用 Django ORM 防止 SQL 注入
3. **CSRF 保护**: 确保 CSRF 中间件启用
4. **数据验证**: 对用户输入进行严格验证

## 备份和恢复

### 备份策略

```bash
# 数据库备份
mysqldump -u username -p database_name > backup.sql

# 静态文件备份
tar -czf static_backup.tar.gz /path/to/static/
```

### 恢复流程

```bash
# 恢复数据库
mysql -u username -p database_name < backup.sql

# 恢复静态文件
tar -xzf static_backup.tar.gz -C /path/to/static/
```

## 版本升级

### 升级步骤

1. 备份数据库和文件
2. 更新代码
3. 运行数据库迁移
4. 收集静态文件
5. 重启服务

### 兼容性检查

确保 Python 和 Django 版本兼容性。