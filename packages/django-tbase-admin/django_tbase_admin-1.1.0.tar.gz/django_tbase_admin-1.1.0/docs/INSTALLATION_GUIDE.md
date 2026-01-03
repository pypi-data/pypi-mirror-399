# Tbase_Admin 模块安装启用配置文档

## 概述

Tbase_Admin 是一个 Django 管理模块，提供性能监控、数据库优化和系统维护功能。本文档详细介绍如何安装、启用和配置该模块。

## 模块功能

### 核心功能
- **性能监控仪表板**: 实时显示数据库表统计信息
- **Session 管理**: 清理过期用户会话
- **Hitcount 清理**: 清理访问统计历史数据
- **数据库优化**: 表结构优化和索引重建
- **管理命令**: 命令行工具支持

### 监控表列表
- `django_session`: 用户会话表
- `hitcount_hit`: 访问记录表
- `hitcount_hit_count`: 访问计数表
- `tbase_post_post`: 文章内容表
- `tbase_page_basepage`: 页面内容表
- `django_admin_log`: 管理日志表

## 安装步骤

### 1. 模块文件结构

确保模块具有以下文件结构：

```
tbase_admin/
├── __init__.py
├── apps.py
├── models.py
├── admin.py
├── views.py
├── urls.py
├── management/
│   └── commands/
│       ├── __init__.py
│       ├── clearsessions.py
│       └── clearhitcount.py
├── templates/
│   └── admin/
│       ├── 404.html
│       ├── 500.html
│       └── performance_dashboard.html
├── static/
│   └── admin/
│       └── css/
└── migrations/
    └── __init__.py
```

### 2. 添加到 Django 项目

#### 2.1 修改 settings.py

在 `INSTALLED_APPS` 中添加模块：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # 添加 Tbase_Admin 模块
    'tbase_admin',
    
    # 其他依赖模块
    'tbase_post',
    'tbase_page',
    'tbase_config',
    'tbase_theme_tailwind',
    'martor',
    'taggit',
    'solo',
    'sitetree',
    'hitcount'
]
```

#### 2.2 配置 URL 路由

在主项目的 `urls.py` 中添加模块路由：

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 添加 Tbase_Admin 路由
    path('tbase-admin/', include('tbase_admin.urls')),
    
    # 其他路由...
]
```

### 3. 数据库配置

确保数据库配置正确：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('db'),
        'USER': os.environ.get('user'),
        'PASSWORD': os.environ.get('password'),
        'HOST': os.environ.get('host'),
        'PORT': os.environ.get('port'),
    }
}
```

### 4. 运行数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations tbase_admin

# 应用迁移
python manage.py migrate
```

### 5. 收集静态文件

```bash
python manage.py collectstatic
```

### 6. 创建超级用户

如果还没有超级用户：

```bash
python manage.py createsuperuser
```

## 配置选项

### 1. Session 配置

在 `settings.py` 中配置 Session：

```python
# Session 配置
SESSION_COOKIE_AGE = 604800  # 7 天
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### 2. 静态文件配置

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```

### 3. 自定义配置（可选）

可以在 `settings.py` 中添加自定义配置：

```python
# Tbase_Admin 配置
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

## 管理命令

### 1. Session 清理命令

创建 `management/commands/clearsessions.py`：

```python
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    help = '清理过期的 Django sessions'

    def handle(self, *args, **options):
        try:
            # 获取清理前数量
            before_count = Session.objects.count()
            
            # 删除过期 sessions
            Session.objects.filter(expire_date__lt=timezone.now()).delete()
            
            # 获取清理后数量
            after_count = Session.objects.count()
            deleted_count = before_count - after_count
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} expired sessions')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing sessions: {str(e)}')
            )
```

### 2. Hitcount 清理命令

创建 `management/commands/clearhitcount.py`：

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from hitcount.models import Hit

class Command(BaseCommand):
    help = '清理指定天数前的 hitcount 数据'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='清理多少天前的数据')
        parser.add_argument('--batch-size', type=int, default=5000, help='批量处理大小')

    def handle(self, *args, **options):
        days = options['days']
        batch_size = options['batch_size']
        
        try:
            cutoff_date = timezone.now() - datetime.timedelta(days=days)
            
            # 获取要删除的记录数
            will_delete = Hit.objects.filter(created__lt=cutoff_date).count()
            
            if will_delete > 0:
                # 执行删除
                Hit.objects.filter(created__lt=cutoff_date).delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {will_delete} hitcount records older than {days} days')
                )
            else:
                self.stdout.write('No records to delete')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing hitcount: {str(e)}')
            )
```

## 权限配置

### 1. 访问权限

所有 Tbase_Admin 功能都需要 `staff_member_required` 权限：

```python
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def performance_dashboard(request):
    # 视图逻辑
    pass
```

### 2. 权限检查

确保用户具有以下权限：
- Django staff 用户 (`is_staff = True`)
- 适当的模型权限（如果需要）

## 访问方式

### 1. 通过 Django Admin

1. 登录 Django Admin (`/admin/`)
2. 在左侧菜单中找到 "性能管理"
3. 点击 "性能优化仪表板"

### 2. 直接访问

直接访问性能仪表板：
- URL: `/tbase-admin/performance/`

### 3. API 访问

获取数据库统计信息：
- URL: `/tbase-admin/api/stats/`
- 方法: GET

## 功能使用

### 1. 查看性能统计

访问性能仪表板查看：
- 各表的记录数量
- 表占用空间大小
- 实时数据刷新

### 2. 清理 Sessions

在仪表板中：
1. 点击 "清理 Sessions" 按钮
2. 确认操作
3. 查看清理结果

### 3. 清理 Hitcount 数据

在仪表板中：
1. 设置清理参数（天数、批量大小）
2. 可选择预览模式
3. 点击 "清理 Hitcount" 按钮
4. 查看清理结果

### 4. 优化数据库表

在仪表板中：
1. 选择要优化的表
2. 点击 "优化选中表" 按钮
3. 等待优化完成

## 依赖模块

确保安装了以下依赖模块：

### 必需模块
- `django-hitcount==1.3.5` - 访问统计
- `martor` - Markdown 编辑器
- `taggit` - 标签系统
- `solo` - 单页应用
- `sitetree` - 站点树结构

### 内置模块
- `django.contrib.sessions`
- `django.contrib.admin`
- `django.contrib.auth`

## 故障排除

### 1. 常见问题

**问题**: 无法访问性能仪表板
```
解决方案: 
1. 确认用户具有 staff 权限
2. 检查 URL 配置是否正确
3. 确认模块已添加到 INSTALLED_APPS
```

**问题**: 数据库统计显示为 0
```
解决方案:
1. 检查数据库连接
2. 确认表名是否正确
3. 检查数据库用户权限
```

**问题**: 清理操作失败
```
解决方案:
1. 检查数据库用户是否有 DELETE 权限
2. 确认表结构是否正确
3. 查看错误日志
```

### 2. 调试方法

启用调试模式：

```python
# settings.py
DEBUG = True
```

查看详细错误信息。

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
            'filename': 'tbase_admin.log',
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

## 性能优化

### 1. 数据库索引

确保以下字段有索引：
- `django_session.session_key`
- `hitcount_hit.created`
- `django_admin_log.action_time`

### 2. 查询优化

使用批量操作：
```python
# 批量删除
Hit.objects.filter(created__lt=cutoff_date).delete()
```

### 3. 缓存配置

可选配置 Redis 缓存：
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## 安全考虑

### 1. 访问控制
- 所有功能需要 staff 权限
- 使用 Django 内置权限系统
- 启用 CSRF 保护

### 2. 数据验证
- 对用户输入进行验证
- 使用参数化查询防止 SQL 注入
- 限制批量操作大小

### 3. 日志记录
- 记录重要操作
- 监控异常情况
- 定期检查日志

## 升级指南

### 1. 备份数据
升级前备份重要数据。

### 2. 更新代码
```bash
git pull origin main
```

### 3. 运行迁移
```bash
python manage.py migrate
```

### 4. 收集静态文件
```bash
python manage.py collectstatic
```

## 维护建议

### 1. 定期清理
- Sessions: 每周清理一次
- Hitcount: 每月清理一次
- 管理日志: 每季度清理一次

### 2. 性能监控
- 监控表大小增长
- 检查查询性能
- 定期优化表结构

### 3. 安全检查
- 定期更新依赖
- 检查权限配置
- 审查访问日志

---

*文档版本: v1.0*  
*最后更新: 2025年12月30日*