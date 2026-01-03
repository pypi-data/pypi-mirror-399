from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sessions.models import Session
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
import datetime
import logging
import time
import psutil
import os

logger = logging.getLogger(__name__)


@staff_member_required
def performance_dashboard(request):
    """性能优化管理仪表板"""
    # 获取数据库统计信息
    stats = get_database_stats_data()
    
    context = {
        'stats': stats,
        'title': '性能优化管理'
    }
    return render(request, 'admin/performance_dashboard.html', context)


@staff_member_required
def get_database_stats(request):
    """获取数据库统计信息的 API"""
    stats = get_database_stats_data()
    return JsonResponse({'success': True, 'stats': stats})


def get_database_stats_data():
    """获取数据库统计数据的内部函数"""
    stats = {}
    
    # 从配置中获取监控表列表，如果没有配置则使用默认列表
    tables_to_check = getattr(settings, 'TBASE_ADMIN', {}).get('MONITORED_TABLES', [
        'django_session',
        'hitcount_hit', 
        'hitcount_hit_count',
        'tbase_post_post',
        'tbase_page_basepage',
        'django_admin_log'
    ])
    
    with connection.cursor() as cursor:
        for table in tables_to_check:
            try:
                # 检查表是否存在
                cursor.execute(f'''
                    SELECT COUNT(*) 
                    FROM information_schema.TABLES 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                ''')
                table_exists = cursor.fetchone()[0] > 0
                
                if not table_exists:
                    stats[table] = {
                        'rows': 0,
                        'size_mb': 0,
                        'status': 'not_exists',
                        'error': '表不存在'
                    }
                    continue
                
                # 获取行数
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                row_count = cursor.fetchone()[0]
                
                # 获取表大小
                cursor.execute(f'''
                    SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2)
                    FROM information_schema.TABLES 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                ''')
                size_result = cursor.fetchone()
                size_mb = float(size_result[0]) if size_result and size_result[0] else 0
                
                # 获取索引大小
                cursor.execute(f'''
                    SELECT ROUND((index_length / 1024 / 1024), 2)
                    FROM information_schema.TABLES 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                ''')
                index_result = cursor.fetchone()
                index_mb = float(index_result[0]) if index_result and index_result[0] else 0
                
                # 获取表引擎信息
                cursor.execute(f'''
                    SELECT ENGINE, TABLE_COLLATION, TABLE_COMMENT
                    FROM information_schema.TABLES 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                ''')
                engine_info = cursor.fetchone()
                
                stats[table] = {
                    'rows': row_count,
                    'size_mb': size_mb,
                    'index_mb': index_mb,
                    'total_mb': size_mb + index_mb,
                    'engine': engine_info[0] if engine_info else 'Unknown',
                    'collation': engine_info[1] if engine_info else 'Unknown',
                    'comment': engine_info[2] if engine_info and engine_info[2] else '',
                    'status': 'ok'
                }
                
                # 添加健康状态检查
                stats[table]['health'] = get_table_health_status(table, row_count, size_mb)
                
            except Exception as e:
                logger.error(f"获取表 {table} 统计信息失败: {str(e)}")
                stats[table] = {
                    'rows': 0,
                    'size_mb': 0,
                    'index_mb': 0,
                    'total_mb': 0,
                    'status': 'error',
                    'error': str(e)
                }
    
    # 添加系统信息
    stats['_system'] = get_system_info()
    
    return stats


def get_table_health_status(table_name, row_count, size_mb):
    """获取表健康状态"""
    # 从配置中获取阈值
    config = getattr(settings, 'TBASE_ADMIN', {})
    thresholds = config.get('ALERT_THRESHOLDS', {
        'SESSION_COUNT_WARNING': 10000,
        'TABLE_SIZE_WARNING_MB': 500,
        'HITCOUNT_COUNT_WARNING': 100000,
    })
    
    health = {
        'status': 'healthy',
        'warnings': [],
        'recommendations': []
    }
    
    # 根据表类型检查特定阈值
    if table_name == 'django_session':
        if row_count > thresholds.get('SESSION_COUNT_WARNING', 10000):
            health['status'] = 'warning'
            health['warnings'].append(f'Sessions 数量过多: {row_count:,}')
            health['recommendations'].append('建议清理过期 sessions')
    
    elif table_name in ['hitcount_hit', 'hitcount_hit_count']:
        if row_count > thresholds.get('HITCOUNT_COUNT_WARNING', 100000):
            health['status'] = 'warning'
            health['warnings'].append(f'Hitcount 记录过多: {row_count:,}')
            health['recommendations'].append('建议清理历史访问记录')
    
    # 通用大小检查
    if size_mb > thresholds.get('TABLE_SIZE_WARNING_MB', 500):
        if health['status'] == 'healthy':
            health['status'] = 'warning'
        health['warnings'].append(f'表大小较大: {size_mb:.2f} MB')
        health['recommendations'].append('考虑优化表结构或清理历史数据')
    
    return health


def get_system_info():
    """获取系统信息"""
    try:
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 数据库连接状态
        db_status = 'connected'
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        except Exception:
            db_status = 'error'
        
        # 缓存状态
        cache_status = 'available'
        try:
            cache.set('tbase_admin_health_check', 'ok', 10)
            cache.get('tbase_admin_health_check')
        except Exception:
            cache_status = 'unavailable'
        
        return {
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'disk_percent': disk.percent,
            'disk_used_gb': round(disk.used / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'db_status': db_status,
            'cache_status': cache_status,
            'process_id': os.getpid(),
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        return {
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@staff_member_required
def cleanup_sessions(request):
    """清理过期 sessions"""
    if request.method == 'POST':
        try:
            # 获取清理前统计
            before_count = Session.objects.count()
            
            # 执行清理
            from django.core.management import call_command
            call_command('clearsessions')
            
            # 获取清理后统计
            after_count = Session.objects.count()
            deleted_count = before_count - after_count
            
            try:
                from django.contrib import messages
                messages.success(request, f'Sessions 清理完成！删除了 {deleted_count:,} 条记录')
            except:
                pass
                
        except Exception as e:
            try:
                from django.contrib import messages
                messages.error(request, f'Sessions 清理失败：{str(e)}')
            except:
                pass
        
        return redirect('tbase_admin:performance_dashboard')


@staff_member_required
def cleanup_hitcount(request):
    """清理 hitcount 数据"""
    if request.method == 'POST':
        days = int(request.POST.get('days', 30))
        batch_size = int(request.POST.get('batch_size', 5000))
        dry_run = request.POST.get('dry_run') == 'on'
        force = request.POST.get('force') == 'on'
        
        try:
            from hitcount.models import Hit
            
            # 获取清理前统计
            before_count = Hit.objects.count()
            
            # 执行清理
            cutoff_date = timezone.now() - datetime.timedelta(days=days)
            
            if dry_run:
                # 预览模式
                will_delete = Hit.objects.filter(created__lt=cutoff_date).count()
                messages.info(request, f'预览模式：将删除 {will_delete:,} 条记录')
            else:
                # 使用管理命令进行清理，支持批量处理
                from django.core.management import call_command
                
                # 构建命令参数
                command_args = [
                    '--days', str(days),
                    '--batch-size', str(batch_size)
                ]
                
                if force:
                    command_args.append('--force')
                
                # 执行清理命令
                call_command('tbase_clearhitcount', *command_args)
                
                # 获取清理后统计
                after_count = Hit.objects.count()
                deleted_count = before_count - after_count
                
                messages.success(request, f'Hitcount 清理完成！删除了 {deleted_count:,} 条记录')
                
        except Exception as e:
            logger.error(f"Hitcount 清理失败: {str(e)}")
            messages.error(request, f'Hitcount 清理失败：{str(e)}')
        
        return redirect('tbase_admin:performance_dashboard')


@staff_member_required
def optimize_tables(request):
    """优化数据库表"""
    if request.method == 'POST':
        tables_to_optimize = request.POST.getlist('tables')
        optimize_type = request.POST.get('optimize_type', 'optimize')  # optimize, analyze, repair
        
        if not tables_to_optimize:
            # 获取配置中的默认表
            tables_to_optimize = getattr(settings, 'TBASE_ADMIN', {}).get('MONITORED_TABLES', [
                'django_session', 'hitcount_hit'
            ])
        
        try:
            start_time = time.time()
            results = []
            
            with connection.cursor() as cursor:
                for table in tables_to_optimize:
                    try:
                        # 检查表是否存在
                        cursor.execute(f'''
                            SELECT COUNT(*) 
                            FROM information_schema.TABLES 
                            WHERE table_schema = DATABASE() 
                            AND table_name = '{table}'
                        ''')
                        table_exists = cursor.fetchone()[0] > 0
                        
                        if not table_exists:
                            results.append({
                                'table': table,
                                'status': 'error',
                                'message': '表不存在'
                            })
                            continue
                        
                        # 获取优化前的表大小
                        cursor.execute(f'''
                            SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2)
                            FROM information_schema.TABLES 
                            WHERE table_schema = DATABASE() 
                            AND table_name = '{table}'
                        ''')
                        size_before = cursor.fetchone()[0] or 0
                        
                        # 执行优化操作
                        if optimize_type == 'optimize':
                            cursor.execute(f'OPTIMIZE TABLE {table}')
                            operation = 'OPTIMIZE'
                        elif optimize_type == 'analyze':
                            cursor.execute(f'ANALYZE TABLE {table}')
                            operation = 'ANALYZE'
                        elif optimize_type == 'repair':
                            cursor.execute(f'REPAIR TABLE {table}')
                            operation = 'REPAIR'
                        else:
                            cursor.execute(f'OPTIMIZE TABLE {table}')
                            operation = 'OPTIMIZE'
                        
                        # 获取优化后的表大小
                        cursor.execute(f'''
                            SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2)
                            FROM information_schema.TABLES 
                            WHERE table_schema = DATABASE() 
                            AND table_name = '{table}'
                        ''')
                        size_after = cursor.fetchone()[0] or 0
                        
                        results.append({
                            'table': table,
                            'status': 'success',
                            'operation': operation,
                            'size_before': size_before,
                            'size_after': size_after,
                            'size_saved': round(size_before - size_after, 2) if size_before > size_after else 0
                        })
                        
                    except Exception as e:
                        logger.error(f"优化表 {table} 失败: {str(e)}")
                        results.append({
                            'table': table,
                            'status': 'error',
                            'message': str(e)
                        })
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            # 统计成功和失败的表
            success_count = sum(1 for r in results if r['status'] == 'success')
            error_count = len(results) - success_count
            total_size_saved = sum(r.get('size_saved', 0) for r in results if r['status'] == 'success')
            
            if error_count == 0:
                messages.success(request, 
                    f'表优化完成！处理了 {success_count} 个表，耗时 {duration} 秒，节省空间 {total_size_saved:.2f} MB')
            else:
                messages.warning(request, 
                    f'表优化部分完成！成功 {success_count} 个，失败 {error_count} 个，耗时 {duration} 秒')
            
            # 将详细结果存入缓存，供前端显示
            cache.set(f'tbase_admin_optimize_results_{request.user.id}', results, 300)
                
        except Exception as e:
            logger.error(f"表优化失败: {str(e)}")
            messages.error(request, f'表优化失败：{str(e)}')
        
        return redirect('tbase_admin:performance_dashboard')


@staff_member_required
def get_optimize_results(request):
    """获取表优化详细结果"""
    results = cache.get(f'tbase_admin_optimize_results_{request.user.id}', [])
    return JsonResponse({'success': True, 'results': results})


@staff_member_required
def cleanup_sessions_advanced(request):
    """高级 Sessions 清理"""
    if request.method == 'POST':
        days = int(request.POST.get('days', 0))  # 0 表示只清理已过期的
        dry_run = request.POST.get('dry_run') == 'on'
        force = request.POST.get('force') == 'on'
        
        try:
            # 获取清理前统计
            before_count = Session.objects.count()
            expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
            
            if dry_run:
                if days > 0:
                    cutoff_date = timezone.now() - datetime.timedelta(days=days)
                    will_delete = Session.objects.filter(expire_date__lt=cutoff_date).count()
                    messages.info(request, f'预览模式：将删除 {will_delete:,} 个 Sessions（包含未过期的）')
                else:
                    messages.info(request, f'预览模式：将删除 {expired_count:,} 个过期 Sessions')
            else:
                # 使用管理命令进行清理
                from django.core.management import call_command
                
                command_args = []
                if dry_run:
                    command_args.append('--dry-run')
                if days > 0:
                    command_args.extend(['--days', str(days)])
                if force:
                    command_args.append('--force')
                
                call_command('tbase_clearsessions', *command_args)
                
                # 获取清理后统计
                after_count = Session.objects.count()
                deleted_count = before_count - after_count
                
                messages.success(request, f'Sessions 清理完成！删除了 {deleted_count:,} 条记录')
                
        except Exception as e:
            logger.error(f"Sessions 清理失败: {str(e)}")
            messages.error(request, f'Sessions 清理失败：{str(e)}')
        
        return redirect('tbase_admin:performance_dashboard')