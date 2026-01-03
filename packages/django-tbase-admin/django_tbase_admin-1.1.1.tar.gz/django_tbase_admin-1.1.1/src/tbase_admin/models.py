from django.db import models


class PerformanceMenuItem(models.Model):
    """
    虚拟模型，用于在 admin 中显示性能管理菜单项
    这个模型不会创建数据库表，仅用于 admin 界面显示
    """
    
    class Meta:
        managed = False  # 不创建数据库表
        verbose_name = "性能管理"
        verbose_name_plural = "性能管理"
        app_label = "tbase_admin"