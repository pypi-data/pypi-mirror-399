from django.apps import AppConfig
from django.core.checks import register, Error, Warning
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
            Error(
                'TBase Admin 需要安装 psutil 包。请运行: pip install psutil',
                hint='pip install psutil',
                id='tbase_admin.E001'
            )
        )
    
    return errors


def check_configuration(app_configs, **kwargs):
    """检查配置"""
    from django.conf import settings
    errors = []
    
    # 检查必要的配置
    if not hasattr(settings, 'TBASE_ADMIN'):
        errors.append(
            Error(
                '请在 settings.py 中添加 TBASE_ADMIN 配置',
                hint='添加 TBASE_ADMIN 配置字典到 settings.py',
                id='tbase_admin.E002'
            )
        )
    else:
        config = settings.TBASE_ADMIN
        
        # 检查必需的配置项
        required_keys = ['MONITORED_TABLES', 'ALERT_THRESHOLDS']
        for key in required_keys:
            if key not in config:
                errors.append(
                    Error(
                        f'TBASE_ADMIN 配置中缺少必需的 {key} 项',
                        hint=f'在 TBASE_ADMIN 配置中添加 {key}',
                        id=f'tbase_admin.E003'
                    )
                )
        
        # 检查表名格式
        tables = config.get('MONITORED_TABLES', [])
        for table in tables:
            if not isinstance(table, str) or not table.replace('_', '').replace('-', '').isalnum():
                errors.append(
                    Warning(
                        f'无效的表名: {table}',
                        hint='表名应只包含字母、数字、下划线和横线',
                        id='tbase_admin.W001'
                    )
                )
    
    return errors
