from django.contrib import admin
from django.urls import reverse
from django.templatetags.static import static


# 自定义 AdminSite
class CustomAdminSite(admin.AdminSite):
    """自定义管理站点，添加性能管理菜单"""
    
    def get_app_list(self, request, app_label=None):
        """
        重写应用列表，添加性能管理菜单
        """
        app_list = super().get_app_list(request, app_label)
        
        # 添加性能管理应用
        performance_app = {
            'name': '性能管理',
            'app_label': 'performance',
            'app_url': reverse('tbase_admin:performance_dashboard'),
            'models': [
                {
                    'name': '性能优化仪表板',
                    'object_name': 'performance_dashboard',
                    'admin_url': reverse('tbase_admin:performance_dashboard'),
                    'view_only': True,
                }
            ]
        }
        
        # 将性能管理添加到应用列表的最前面
        app_list.insert(0, performance_app)
        
        return app_list


# 创建自定义站点实例
custom_admin = CustomAdminSite('custom_admin')


# 修改默认 admin 站点的标题
admin.site.site_title = "后台管理"
admin.site.site_header = "内容管理系统"
admin.site.index_title = "管理"


# 添加自定义模板标签
@register.inclusion_tag('admin/performance_link.html')
def performance_management_link():
    """渲染性能管理链接"""
    return {
        'url': reverse('tbase_admin:performance_dashboard')
    }