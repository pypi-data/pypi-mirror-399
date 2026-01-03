from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.utils import timezone
import datetime
import json


class TBaseAdminTestCase(TestCase):
    """TBase Admin 功能测试"""
    
    def setUp(self):
        """测试初始化"""
        # 创建管理员用户
        self.user = User.objects.create_superuser(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试客户端
        self.client = Client()
        self.client.login(username='testadmin', password='testpass123')
        
        # 创建一些测试 sessions
        for i in range(5):
            session = Session.objects.create(
                session_data='test_data',
                expire_date=timezone.now() - datetime.timedelta(days=i+1)
            )
    
    def test_performance_dashboard_view(self):
        """测试性能仪表板页面"""
        url = reverse('tbase_admin:performance_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '性能优化管理')
        self.assertContains(response, '数据库统计')
        self.assertContains(response, '系统状态')
    
    def test_get_database_stats_api(self):
        """测试数据库统计 API"""
        url = reverse('tbase_admin:get_database_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
        self.assertIn('_system', data['stats'])
    
    def test_cleanup_sessions(self):
        """测试 Sessions 清理功能"""
        # 获取清理前的数量
        before_count = Session.objects.count()
        
        url = reverse('tbase_admin:cleanup_sessions')
        response = self.client.post(url)
        
        # 应该重定向回仪表板
        self.assertEqual(response.status_code, 302)
        
        # 检查是否清理了过期 sessions
        after_count = Session.objects.count()
        self.assertLess(after_count, before_count)
    
    def test_cleanup_sessions_advanced(self):
        """测试高级 Sessions 清理功能"""
        # 获取清理前的数量
        before_count = Session.objects.count()
        
        url = reverse('tbase_admin:cleanup_sessions_advanced')
        response = self.client.post(url, {
            'days': 7,
            'dry_run': 'on'
        })
        
        # 应该重定向回仪表板
        self.assertEqual(response.status_code, 302)
        
        # 预览模式不应该删除数据
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
    
    def test_cleanup_hitcount_dry_run(self):
        """测试 Hitcount 清理（预览模式）"""
        url = reverse('tbase_admin:cleanup_hitcount')
        response = self.client.post(url, {
            'days': 30,
            'batch_size': 1000,
            'dry_run': 'on'
        })
        
        # 应该重定向回仪表板
        self.assertEqual(response.status_code, 302)
    
    def test_optimize_tables(self):
        """测试表优化功能"""
        url = reverse('tbase_admin:optimize_tables')
        response = self.client.post(url, {
            'tables': ['django_session'],
            'optimize_type': 'analyze'  # 使用 analyze 避免长时间锁定
        })
        
        # 应该重定向回仪表板
        self.assertEqual(response.status_code, 302)
    
    def test_get_optimize_results(self):
        """测试获取优化结果 API"""
        url = reverse('tbase_admin:get_optimize_results')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertIsInstance(data['results'], list)


class ManagementCommandsTestCase(TestCase):
    """管理命令测试"""
    
    def test_clearsessions_command(self):
        """测试清理 sessions 命令"""
        # 创建一个过期 session
        session = Session.objects.create(
            session_data='test_data',
            expire_date=timezone.now() - datetime.timedelta(days=1)
        )
        
        from django.core.management import call_command
        out = call_command('tbase_clearsessions', '--dry-run')
        
        # 命令应该成功执行
        self.assertIsNotNone(out)
    
    def test_clearhitcount_command(self):
        """测试清理 hitcount 命令"""
        from django.core.management import call_command
        
        # 测试预览模式
        out = call_command('tbase_clearhitcount', '--dry-run', '--days=30')
        self.assertIsNotNone(out)
    
    def test_optimize_tables_command(self):
        """测试表优化命令"""
        from django.core.management import call_command
        
        # 测试预览模式
        out = call_command('tbase_optimize_tables', '--dry-run', '--operation=check')
        self.assertIsNotNone(out)


class ConfigurationTestCase(TestCase):
    """配置测试"""
    
    def test_default_configuration(self):
        """测试默认配置"""
        from django.conf import settings
        
        # 检查是否有 TBASE_ADMIN 配置
        self.assertTrue(hasattr(settings, 'TBASE_ADMIN'))
        
        config = settings.TBASE_ADMIN
        
        # 检查必需的配置项
        self.assertIn('MONITORED_TABLES', config)
        self.assertIn('ALERT_THRESHOLDS', config)
        self.assertIsInstance(config['MONITORED_TABLES'], list)
        self.assertIsInstance(config['ALERT_THRESHOLDS'], dict)


class SecurityTestCase(TestCase):
    """安全性测试"""
    
    def setUp(self):
        """测试初始化"""
        # 创建普通用户（非管理员）
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_admin_required(self):
        """测试需要管理员权限"""
        url = reverse('tbase_admin:performance_dashboard')
        response = self.client.get(url)
        
        # 普通用户应该被重定向到登录页面
        self.assertEqual(response.status_code, 302)
    
    def test_unauthenticated_access(self):
        """测试未认证访问"""
        self.client.logout()
        url = reverse('tbase_admin:performance_dashboard')
        response = self.client.get(url)
        
        # 未认证用户应该被重定向到登录页面
        self.assertEqual(response.status_code, 302)