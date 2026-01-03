"""
Django TBase Admin - Performance Monitoring and Database Optimization

A Django admin module that provides comprehensive performance monitoring,
database statistics, session management, and optimization tools.
"""

__version__ = "1.0.0"
__author__ = "Terry Chan"
__email__ = "terry@example.com"
__description__ = "Django admin module for performance monitoring and database optimization"

# Default configuration
default_config = {
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