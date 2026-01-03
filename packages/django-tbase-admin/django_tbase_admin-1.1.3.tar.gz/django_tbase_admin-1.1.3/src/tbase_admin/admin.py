from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import PerformanceMenuItem

# Register your models here.
admin.site.site_title = "后台管理"
admin.site.site_header = "内容管理系统"
admin.site.index_title = "管理"


# 自定义 AdminSite 类来添加性能管理菜单
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        """
        重写应用列表，添加性能管理菜单
        """
        app_list = super().get_app_list(request, app_label)
        
        # 添加性能管理应用到列表最前面
        performance_app = {
            'name': '性能管理',
            'app_label': 'performance',
            'app_url': reverse('tbase_admin:performance_dashboard'),
            'has_module_perms': True,
            'models': [
                {
                    'name': '性能优化仪表板',
                    'object_name': 'performance_dashboard',
                    'admin_url': reverse('tbase_admin:performance_dashboard'),
                    'view_only': True,
                }
            ]
        }
        
        app_list.insert(0, performance_app)
        return app_list


# 创建自定义 admin 站点实例
custom_admin = CustomAdminSite(name='custom_admin')


# 注册性能管理虚拟模型
class PerformanceAdmin(admin.ModelAdmin):
    """
    性能管理的 admin 类
    """
    
    def has_add_permission(self, request):
        return False  # 不允许添加
    
    def has_change_permission(self, request, obj=None):
        return False  # 不允许修改
    
    def has_delete_permission(self, request, obj=None):
        return False  # 不允许删除
    
    def changelist_view(self, request, extra_context=None):
        """
        重写列表视图，重定向到性能管理页面
        """
        from django.shortcuts import redirect
        return redirect('tbase_admin:performance_dashboard')


# 注册到默认 admin 站点
admin.site.register(PerformanceMenuItem, PerformanceAdmin)


# 添加自定义模板标签来显示性能管理链接
from django.template import Library
register = Library()

@register.simple_tag
def performance_management_link():
    """生成性能管理链接"""
    try:
        from django.urls import reverse
        url = reverse('tbase_admin:performance_dashboard')
        return f'<a href="{url}" class="model">性能优化仪表板</a>'
    except:
        return '<a href="/admin/performance/" class="model">性能优化仪表板</a>'






