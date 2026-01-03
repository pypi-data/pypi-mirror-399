#!/usr/bin/env python
"""
简单的功能测试脚本
"""
import os
import sys
import django
from django.conf import settings

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置 Django
if not settings.configured:
    settings.configure(
        SECRET_KEY='test-secret-key',
        DEBUG=True,
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'tbase_admin',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        TBASE_ADMIN={
            'MONITORED_TABLES': ['django_session'],
            'ALERT_THRESHOLDS': {
                'SESSION_COUNT_WARNING': 10000,
                'TABLE_SIZE_WARNING_MB': 500,
            }
        },
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        },
        USE_TZ=True,
    )

django.setup()

def test_imports():
    """测试导入"""
    try:
        from tbase_admin.views import performance_dashboard, get_database_stats
        from tbase_admin.management.commands.tbase_clearsessions import Command as ClearSessionsCommand
        from tbase_admin.management.commands.tbase_clearhitcount import Command as ClearHitcountCommand
        from tbase_admin.management.commands.tbase_optimize_tables import Command as OptimizeTablesCommand
        print("✅ 所有导入测试通过")
        return True
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        return False

def test_configuration():
    """测试配置"""
    try:
        from django.conf import settings
        
        # 检查 TBASE_ADMIN 配置
        assert hasattr(settings, 'TBASE_ADMIN')
        config = settings.TBASE_ADMIN
        
        # 检查必需配置项
        assert 'MONITORED_TABLES' in config
        assert 'ALERT_THRESHOLDS' in config
        assert isinstance(config['MONITORED_TABLES'], list)
        assert isinstance(config['ALERT_THRESHOLDS'], dict)
        
        print("✅ 配置测试通过")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_views():
    """测试视图函数"""
    try:
        from tbase_admin.views import get_database_stats_data
        
        # 测试数据库统计函数
        stats = get_database_stats_data()
        assert isinstance(stats, dict)
        assert '_system' in stats
        
        print("✅ 视图函数测试通过")
        return True
    except Exception as e:
        print(f"❌ 视图函数测试失败: {e}")
        return False

def test_management_commands():
    """测试管理命令"""
    try:
        from tbase_admin.management.commands.tbase_clearsessions import Command as ClearSessionsCommand
        from tbase_admin.management.commands.tbase_clearhitcount import Command as ClearHitcountCommand
        from tbase_admin.management.commands.tbase_optimize_tables import Command as OptimizeTablesCommand
        
        # 测试命令实例化
        clear_sessions = ClearSessionsCommand()
        clear_hitcount = ClearHitcountCommand()
        optimize_tables = OptimizeTablesCommand()
        
        assert clear_sessions.help
        assert clear_hitcount.help
        assert optimize_tables.help
        
        print("✅ 管理命令测试通过")
        return True
    except Exception as e:
        print(f"❌ 管理命令测试失败: {e}")
        return False

def test_urls():
    """测试 URL 配置"""
    try:
        from django.urls import reverse
        from tbase_admin import urls as tbase_urls
        
        # 检查 URL 模式
        urlpatterns = tbase_urls.urlpatterns
        assert len(urlpatterns) > 0
        
        print("✅ URL 配置测试通过")
        return True
    except Exception as e:
        print(f"❌ URL 配置测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始 TBase Admin 功能测试...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_views,
        test_management_commands,
        test_urls,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！TBase Admin 模块功能正常。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)