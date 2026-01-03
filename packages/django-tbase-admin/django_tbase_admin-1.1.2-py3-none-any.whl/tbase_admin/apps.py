from django.apps import AppConfig
from django.core.checks import register
import logging

logger = logging.getLogger(__name__)


class TbaseAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tbase_admin'
    verbose_name = 'TBase 管理模块'
    
    def ready(self):
        """应用启动时的初始化操作"""
        # 注册系统检查
        register(check_dependencies)
        register(check_configuration)
        
        # 初始化日志
        logger.info('TBase Admin 模块已启动')


def check_dependencies(app_configs, **kwargs):
    """检查依赖包"""
    errors = []
    
    try:
        import psutil
    except ImportError:
        errors.append(
            'TBase Admin 需要安装 psutil 包。请运行: pip install psutil'
        )
    
    return errors


def check_configuration(app_configs, **kwargs):
    """检查配置"""
    from django.conf import settings
    errors = []
    
    # 检查必要的配置
    if not hasattr(settings, 'TBASE_ADMIN'):
        errors.append(
            '请在 settings.py 中添加 TBASE_ADMIN 配置'
        )
    else:
        config = settings.TBASE_ADMIN
        
        # 检查必需的配置项
        required_keys = ['MONITORED_TABLES', 'ALERT_THRESHOLDS']
        for key in required_keys:
            if key not in config:
                errors.append(f'TBASE_ADMIN 配置中缺少必需的 {key} 项')
        
        # 检查表名格式
        tables = config.get('MONITORED_TABLES', [])
        for table in tables:
            if not isinstance(table, str) or not table.isidentifier():
                errors.append(f'无效的表名: {table}')
    
    return errors
