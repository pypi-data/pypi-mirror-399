from django.core.management.base import BaseCommand
from django.db import connection
import time


class Command(BaseCommand):
    help = '数据库表优化管理命令'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tables',
            nargs='*',
            help='指定要优化的表名，如果不指定则使用配置中的默认表',
        )
        parser.add_argument(
            '--operation',
            choices=['optimize', 'analyze', 'repair', 'check'],
            default='optimize',
            help='操作类型：optimize(优化), analyze(分析), repair(修复), check(检查)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，跳过安全检查',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，只显示将要执行的操作',
        )

    def handle(self, *args, **options):
        tables = options['tables']
        operation = options['operation']
        force = options['force']
        dry_run = options['dry_run']
        
        # 获取表列表
        if not tables:
            from django.conf import settings
            tables = getattr(settings, 'TBASE_ADMIN', {}).get('MONITORED_TABLES', [
                'django_session', 'hitcount_hit'
            ])
        
        # 验证表是否存在
        valid_tables = []
        for table in tables:
            if self._table_exists(table):
                valid_tables.append(table)
            else:
                self.stdout.write(
                    self.style.WARNING(f'表 {table} 不存在，跳过')
                )
        
        if not valid_tables:
            self.stdout.write(
                self.style.ERROR('没有找到有效的表进行优化')
            )
            return
        
        # 显示操作计划
        self.stdout.write(f'=== 数据库表 {operation.upper()} 计划 ===')
        self.stdout.write(f'操作类型: {operation.upper()}')
        self.stdout.write(f'目标表: {", ".join(valid_tables)}')
        
        # 获取表大小信息
        total_size_before = 0
        for table in valid_tables:
            size_info = self._get_table_size(table)
            total_size_before += size_info['total_mb']
            self.stdout.write(f'- {table}: {size_info["total_mb"]:.2f} MB (数据: {size_info["data_mb"]:.2f} MB, 索引: {size_info["index_mb"]:.2f} MB)')
        
        self.stdout.write(f'总大小: {total_size_before:.2f} MB')
        
        # 安全检查
        if not force and operation in ['repair', 'optimize']:
            if not self._safety_check(valid_tables):
                self.stdout.write(
                    self.style.ERROR('安全检查失败，使用 --force 强制执行')
                )
                return
        
        if not dry_run and not force:
            confirm = input(f'\n确认执行 {operation.upper()} 操作？(y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('操作已取消')
                return
        
        # 执行操作
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] 预览模式，不会实际执行操作'))
        else:
            start_time = time.time()
            results = self._execute_operation(valid_tables, operation)
            end_time = time.time()
            
            # 显示结果
            self.stdout.write(f'\n=== 操作完成 ===')
            self.stdout.write(f'耗时: {end_time - start_time:.2f} 秒')
            
            success_count = sum(1 for r in results if r['status'] == 'success')
            error_count = len(results) - success_count
            
            if error_count == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'所有 {success_count} 个表操作成功')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'成功 {success_count} 个，失败 {error_count} 个')
                )
            
            # 显示详细结果
            if operation == 'optimize':
                total_size_after = 0
                total_saved = 0
                
                for result in results:
                    if result['status'] == 'success':
                        size_after = result.get('size_after', 0)
                        total_size_after += size_after
                        saved = result.get('size_before', 0) - size_after
                        total_saved += saved
                        
                        self.stdout.write(
                            f'- {result["table"]}: {result["size_before"]:.2f} MB → {size_after:.2f} MB'
                            + (f' (节省 {saved:.2f} MB)' if saved > 0 else '')
                        )
                
                if total_saved > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'总计节省空间: {total_saved:.2f} MB')
                    )
            
            # 显示错误信息
            for result in results:
                if result['status'] == 'error':
                    self.stdout.write(
                        self.style.ERROR(f'- {result["table"]}: {result["error"]}')
                    )

    def _table_exists(self, table_name):
        """检查表是否存在"""
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            ''', [table_name])
            return cursor.fetchone()[0] > 0

    def _get_table_size(self, table_name):
        """获取表大小信息"""
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    ROUND((data_length / 1024 / 1024), 2) as data_mb,
                    ROUND((index_length / 1024 / 1024), 2) as index_mb,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) as total_mb
                FROM information_schema.TABLES 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            ''', [table_name])
            
            result = cursor.fetchone()
            if result:
                return {
                    'data_mb': float(result[0]) if result[0] else 0,
                    'index_mb': float(result[1]) if result[1] else 0,
                    'total_mb': float(result[2]) if result[2] else 0
                }
            return {'data_mb': 0, 'index_mb': 0, 'total_mb': 0}

    def _safety_check(self, tables):
        """安全检查"""
        self.stdout.write('执行安全检查...')
        
        with connection.cursor() as cursor:
            for table in tables:
                # 检查表是否被锁定
                cursor.execute(f'SHOW OPEN TABLES WHERE `{table}` LIKE "{table}" AND In_use > 0')
                if cursor.fetchone():
                    self.stdout.write(
                        self.style.ERROR(f'表 {table} 正在被使用，无法执行优化操作')
                    )
                    return False
                
                # 检查表大小，避免对过大的表进行操作
                size_info = self._get_table_size(table)
                if size_info['total_mb'] > 1000:  # 超过1GB的表需要特别小心
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ 表 {table} 较大 ({size_info["total_mb"]:.2f} MB)，可能需要较长时间')
                    )
        
        return True

    def _execute_operation(self, tables, operation):
        """执行数据库操作"""
        results = []
        
        with connection.cursor() as cursor:
            for table in tables:
                result = {'table': table, 'status': 'success'}
                
                try:
                    # 获取操作前的大小
                    size_before = self._get_table_size(table)['total_mb']
                    result['size_before'] = size_before
                    
                    # 执行操作
                    if operation == 'optimize':
                        cursor.execute(f'OPTIMIZE TABLE {table}')
                    elif operation == 'analyze':
                        cursor.execute(f'ANALYZE TABLE {table}')
                    elif operation == 'repair':
                        cursor.execute(f'REPAIR TABLE {table}')
                    elif operation == 'check':
                        cursor.execute(f'CHECK TABLE {table}')
                    
                    # 获取操作后的大小（仅对 OPTIMIZE 操作有意义）
                    if operation == 'optimize':
                        size_after = self._get_table_size(table)['total_mb']
                        result['size_after'] = size_after
                    
                    self.stdout.write(f'✓ {table} {operation.upper()} 完成')
                    
                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = str(e)
                    self.stdout.write(
                        self.style.ERROR(f'✗ {table} {operation.upper()} 失败: {str(e)}')
                    )
                
                results.append(result)
                
                # 短暂休息，避免数据库压力过大
                time.sleep(0.1)
        
        return results