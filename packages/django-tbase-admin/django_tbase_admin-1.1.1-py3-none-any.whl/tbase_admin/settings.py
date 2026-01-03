"""
Django TBase Admin 配置文件

将以下配置添加到您的 Django settings.py 文件中：
"""

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
        # Session 数量警告阈值
        'SESSION_COUNT_WARNING': 10000,
        'SESSION_COUNT_CRITICAL': 50000,
        
        # 表大小警告阈值 (MB)
        'TABLE_SIZE_WARNING_MB': 500,
        'TABLE_SIZE_CRITICAL_MB': 1000,
        
        # Hitcount 记录数警告阈值
        'HITCOUNT_COUNT_WARNING': 100000,
        'HITCOUNT_COUNT_CRITICAL': 500000,
        
        # 内存使用警告阈值 (%)
        'MEMORY_WARNING': 70,
        'MEMORY_CRITICAL': 85,
        
        # 磁盘使用警告阈值 (%)
        'DISK_WARNING': 80,
        'DISK_CRITICAL': 90,
    },
    
    # 自动清理配置
    'AUTO_CLEANUP': {
        'enabled': False,  # 是否启用自动清理
        'sessions_interval_hours': 24,  # Sessions 清理间隔（小时）
        'hitcount_interval_days': 30,   # Hitcount 清理间隔（天）
        'optimize_interval_days': 7,    # 表优化间隔（天）
    },
    
    # 性能监控配置
    'PERFORMANCE_MONITORING': {
        'enabled': True,  # 是否启用性能监控
        'retention_days': 30,  # 监控数据保留天数
        'alert_email': None,   # 警告邮件地址
    },
    
    # 安全配置
    'SECURITY': {
        'require_confirmation': True,  # 是否需要确认操作
        'max_batch_size': 10000,       # 最大批量大小
        'allow_optimize_large_tables': False,  # 是否允许优化大表
        'large_table_threshold_mb': 1000,      # 大表阈值
    }
}

# 缓存配置（可选）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tbase_admin_cache',
        'TIMEOUT': 300,  # 5分钟
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# 日志配置（可选）
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/tbase_admin.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'tbase_admin': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 依赖包要求
# 注意：确保以下包已安装：
# - psutil>=5.8.0 (系统监控)
# - django-hitcount (如果使用 hitcount 功能)
# - django-taggit (如果使用标签功能)