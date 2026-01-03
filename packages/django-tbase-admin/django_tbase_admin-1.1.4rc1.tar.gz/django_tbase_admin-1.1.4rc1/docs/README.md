# Tbase_Admin 模块使用说明文档

## 概述

Tbase_Admin 是一个 Django 管理后台模块，专门用于系统性能监控和数据库优化。该模块提供了直观的 Web 界面，让管理员可以轻松查看系统状态、清理过期数据和优化数据库性能。

## 主要功能

### 1. 性能监控仪表板
- 实时显示数据库表统计信息
- 监控表大小和记录数量
- 提供可视化性能指标

### 2. Session 管理
- 查看当前活跃 sessions 数量
- 清理过期 sessions
- 释放数据库空间

### 3. Hitcount 数据管理
- 统计访问记录数据
- 按时间范围清理历史数据
- 支持批量操作

### 4. 数据库优化
- 表优化操作
- 索引重建
- 查询性能分析

## 访问方式

### 登录管理后台

1. 使用超级用户账号登录 Django Admin
2. 访问 `/admin/` 或 `/tbase-admin/`
3. 在左侧菜单中找到 "性能管理" 选项

### 直接访问性能仪表板

URL: `/tbase-admin/performance/`

## 功能详解

### 性能仪表板

仪表板显示以下信息：

- **数据库表统计**: 每个表的记录数和占用空间
- **实时数据**: 点击 "刷新" 获取最新统计
- **快速操作**: 提供常用清理和优化操作的快捷入口

#### 表统计信息说明

| 表名 | 说明 | 监控指标 |
|------|------|----------|
| django_session | 用户会话 | 记录数、大小 |
| hitcount_hit | 访问统计 | 记录数、大小 |
| hitcount_hit_count | 访问计数 | 记录数、大小 |
| tbase_post_post | 文章内容 | 记录数、大小 |
| tbase_page_basepage | 页面内容 | 记录数、大小 |
| django_admin_log | 管理日志 | 记录数、大小 |

### Session 清理

#### 操作步骤

1. 在性能仪表板中找到 "Session 管理" 部分
2. 点击 "清理 Sessions" 按钮
3. 确认操作
4. 查看清理结果

#### 清理说明

- 自动识别并删除过期 sessions
- 显示删除的记录数量
- 操作完成后自动刷新统计数据

#### 安全提示

- 清理操作不可逆
- 建议在低峰期执行
- 清理前查看当前活跃用户数

### Hitcount 数据清理

#### 操作步骤

1. 在性能仪表板中找到 "Hitcount 管理" 部分
2. 设置清理参数：
   - **天数**: 删除多少天前的数据
   - **批量大小**: 每次处理的记录数
   - **预览模式**: 只显示将要删除的记录数，不实际删除
3. 点击 "清理 Hitcount" 按钮
4. 查看清理结果

#### 参数说明

- **天数**: 默认 30 天，可根据需要调整
- **批量大小**: 默认 5000，大数据量时可适当增大
- **预览模式**: 建议首次使用时开启，确认无误后再正式清理

#### 最佳实践

- 定期清理（建议每月一次）
- 保留最近 3-6 个月的数据用于分析
- 在业务低峰期执行清理操作

### 数据库表优化

#### 操作步骤

1. 在性能仪表板中找到 "表优化" 部分
2. 选择要优化的表（可多选）
3. 点击 "优化选中表" 按钮
4. 等待优化完成

#### 优化效果

- 重建表索引
- 回收碎片空间
- 提升查询性能
- 减少存储空间占用

#### 注意事项

- 优化过程中表可能被锁定
- 大表优化需要较长时间
- 建议在维护窗口期执行

## API 接口

### 获取数据库统计

**接口**: `GET /tbase-admin/api/stats/`

**响应格式**:
```json
{
    "success": true,
    "stats": {
        "django_session": {
            "rows": 1234,
            "size_mb": 2.5
        },
        "hitcount_hit": {
            "rows": 56789,
            "size_mb": 15.2
        }
    }
}
```

### 清理 Sessions

**接口**: `POST /tbase-admin/cleanup/sessions/`

**参数**: 无

**响应**: 重定向到仪表板并显示操作结果

### 清理 Hitcount

**接口**: `POST /tbase-admin/cleanup/hitcount/`

**参数**:
- `days`: 清理天数
- `batch_size`: 批量大小
- `dry_run`: 是否预览模式

**响应**: 重定向到仪表板并显示操作结果

### 优化表

**接口**: `POST /tbase-admin/optimize/tables/`

**参数**:
- `tables`: 要优化的表名列表

**响应**: 重定向到仪表板并显示操作结果

## 权限管理

### 访问权限

- 必须是 Django staff 用户
- 建议只给管理员分配权限
- 可通过 Django 权限系统精细控制

### 权限配置

```python
# settings.py
TBASE_ADMIN_PERMISSIONS = {
    'view_dashboard': ['admin', 'manager'],
    'cleanup_sessions': ['admin'],
    'cleanup_hitcount': ['admin'],
    'optimize_tables': ['admin'],
}
```

## 监控和告警

### 性能阈值

建议设置以下监控阈值：

- Sessions 数量 > 10,000
- 单表大小 > 500MB
- Hitcount 记录数 > 100,000

### 告警配置

可以通过 Django 信号或外部监控系统设置告警：

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sessions.models import Session

@receiver(post_save, sender=Session)
def session_count_check(sender, **kwargs):
    count = Session.objects.count()
    if count > 10000:
        # 发送告警
        pass
```

## 最佳实践

### 定期维护

1. **每日**: 检查性能仪表板
2. **每周**: 清理过期 sessions
3. **每月**: 清理历史 hitcount 数据
4. **每季度**: 执行表优化

### 数据保留策略

- Sessions: 保留 7 天
- Hitcount: 保留 90 天
- 管理日志: 保留 1 年
- 其他数据: 根据业务需要确定

### 性能优化建议

1. 定期执行表优化
2. 监控数据库大小增长
3. 及时清理临时数据
4. 优化数据库查询

## 故障排除

### 常见问题

**Q: 清理操作失败怎么办？**
A: 检查数据库权限，确保用户有 DELETE 权限

**Q: 表优化时间太长？**
A: 大表优化需要时间，建议在维护窗口期执行

**Q: 统计数据不准确？**
A: 点击 "刷新" 按钮获取最新数据

**Q: 无法访问性能仪表板？**
A: 确认用户具有 staff 权限且已登录

### 错误代码

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| 403 | 权限不足 | 联系管理员分配权限 |
| 404 | 页面不存在 | 检查 URL 配置 |
| 500 | 服务器错误 | 查看错误日志 |

### 日志查看

```bash
# 查看 Django 日志
tail -f /var/log/django/error.log

# 查看数据库日志
tail -f /var/log/mysql/error.log
```

## 扩展开发

### 自定义监控表

在 `views.py` 中修改 `tables_to_check` 列表：

```python
tables_to_check = [
    'django_session',
    'hitcount_hit',
    'your_custom_table',  # 添加自定义表
]
```

### 添加新的清理功能

1. 在 `views.py` 中添加新的视图函数
2. 在 `urls.py` 中添加 URL 路由
3. 在模板中添加操作按钮

### 自定义仪表板

修改 `templates/admin/performance_dashboard.html` 模板文件，添加自定义图表和指标。

## 技术支持

如遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查 Django 和数据库日志
3. 联系系统管理员
4. 提交 Issue 到项目仓库

---

*最后更新: 2025年12月30日*