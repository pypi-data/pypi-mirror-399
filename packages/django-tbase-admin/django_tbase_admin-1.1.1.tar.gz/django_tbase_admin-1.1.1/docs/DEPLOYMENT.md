# Tbase_Admin 模块部署文档

## 概述

Tbase_Admin 是一个 Django 管理后台模块，提供性能优化管理功能，包括数据库统计信息查看、过期数据清理、表优化等操作。

## 系统要求

- Python 3.8+
- Django 3.2+
- MySQL 5.7+ 或 PostgreSQL 10+
- Django Hitcount 应用（用于访问统计）

## 安装步骤

### 1. 添加到 Django 应用

在 `settings.py` 中的 `INSTALLED_APPS` 添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'tbase_admin',
    'hitcount',  # 如果需要 hitcount 功能
]
```

### 2. URL 配置

在主项目的 `urls.py` 中包含 tbase_admin 的 URL：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他 URL
    path('admin/', admin.site.urls),
    path('tbase_admin/', include('tbase_admin.urls')),
]
```

### 3. 数据库迁移

```bash
python manage.py makemigrations tbase_admin
python manage.py migrate
```

### 4. 创建超级用户（如果还没有）

```bash
python manage.py createsuperuser
```

## 配置选项

### 自定义 Admin 站点

如果需要使用自定义管理站点，在 `urls.py` 中：

```python
from tbase_admin.custom_admin import custom_admin

urlpatterns = [
    path('custom-admin/', custom_admin.urls),
]
```

### 性能监控表配置

在 `views.py` 中的 `tables_to_check` 列表可以根据需要调整：

```python
tables_to_check = [
    'django_session',
    'hitcount_hit', 
    'hitcount_hit_count',
    'tbase_post_post',      # 根据实际表名调整
    'tbase_page_basepage',  # 根据实际表名调整
    'django_admin_log'
]
```

## 权限要求

- 所有功能都需要 `staff_member_required` 装饰器
- 建议只给管理员权限访问 `/tbase_admin/` 路径
- 数据库操作需要相应的数据库权限

## 安全注意事项

1. **访问控制**: 确保只有授权用户可以访问管理界面
2. **数据库权限**: 应用数据库用户需要有 SELECT, DELETE, OPTIMIZE 权限
3. **日志记录**: 建议启用 Django 的日志记录功能
4. **定期备份**: 在执行清理操作前建议备份数据

## 性能优化建议

1. **定期清理**: 设置定时任务定期清理过期 sessions 和 hitcount 数据
2. **索引优化**: 确保相关表有适当的索引
3. **监控告警**: 设置数据库大小和行数的监控告警
4. **批量操作**: 对于大量数据清理，使用批量操作避免内存溢出

## 故障排除

### 常见问题

1. **表不存在错误**: 检查 `tables_to_check` 列表中的表名是否正确
2. **权限不足**: 确保数据库用户有足够的权限
3. **模板找不到**: 确保 `templates` 目录在正确的位置

### 调试模式

在 `settings.py` 中启用调试：

```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'tbase_admin': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## 维护任务

### 定期清理脚本

可以创建管理命令来定期执行清理任务：

```bash
# 清理过期 sessions
python manage.py clearsessions

# 清理旧的 hitcount 数据（30天前）
python manage.py cleanup_hitcount --days=30
```

### 监控指标

建议监控以下指标：
- 数据库表大小
- sessions 表行数
- hitcount 表行数
- 查询响应时间