from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
import datetime
import time


class Command(BaseCommand):
    help = '优化的 hitcount 数据清理命令，支持批量删除和性能监控'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='清理多少天前的数据（默认30天）',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='批量删除的批次大小（默认5000）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际删除数据',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，不询问确认',
        )
        parser.add_argument(
            '--min-records',
            type=int,
            default=10000,
            help='最少记录数阈值，低于此值不执行清理（默认10000）',
        )

    def handle(self, *args, **options):
        days = options['days']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        force = options['force']
        min_records = options['min_records']
        
        start_time = time.time()
        
        # 检查表状态
        total_before = self._get_record_count()
        
        if total_before < min_records:
            self.stdout.write(
                self.style.WARNING(f'当前记录数 ({total_before:,}) 少于阈值 ({min_records:,})，跳过清理')
            )
            return
        
        # 计算清理范围
        cutoff_date = timezone.now() - datetime.timedelta(days=days)
        to_delete_count = self._get_records_before_count(cutoff_date)
        
        if to_delete_count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'没有找到超过 {days} 天的记录需要清理')
            )
            return
        
        # 显示清理计划
        self.stdout.write(f'=== Hitcount 数据清理计划 ===')
        self.stdout.write(f'清理截止日期: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'当前总记录数: {total_before:,}')
        self.stdout.write(f'将删除记录数: {to_delete_count:,}')
        self.stdout.write(f'保留记录数: {total_before - to_delete_count:,}')
        self.stdout.write(f'批次大小: {batch_size:,}')
        self.stdout.write(f'预计批次数: {(to_delete_count + batch_size - 1) // batch_size:,}')
        
        if not dry_run and not force:
            confirm = input('\n确认执行清理？(y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('清理操作已取消')
                return
        
        # 执行清理
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] 预览模式，不会实际删除数据'))
        else:
            deleted_count = self._batch_delete(cutoff_date, batch_size)
            
            # 显示结果
            end_time = time.time()
            duration = end_time - start_time
            total_after = self._get_record_count()
            
            self.stdout.write(f'\n=== 清理完成 ===')
            self.stdout.write(self.style.SUCCESS(f'成功删除 {deleted_count:,} 条记录'))
            self.stdout.write(f'剩余记录数: {total_after:,}')
            self.stdout.write(f'耗时: {duration:.2f} 秒')
            
            if duration > 0:
                speed = deleted_count / duration
                self.stdout.write(f'删除速度: {speed:.0f} 记录/秒')

    def _get_record_count(self):
        """获取当前记录总数"""
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM hitcount_hit')
            return cursor.fetchone()[0]

    def _get_records_before_count(self, cutoff_date):
        """获取指定日期之前的记录数"""
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM hitcount_hit WHERE created < %s',
                [cutoff_date]
            )
            return cursor.fetchone()[0]

    def _batch_delete(self, cutoff_date, batch_size):
        """批量删除记录"""
        total_deleted = 0
        batch_num = 0
        
        with connection.cursor() as cursor:
            while True:
                # 使用优化的索引进行批量删除
                cursor.execute('''
                    DELETE FROM hitcount_hit 
                    WHERE created < %s 
                    LIMIT %s
                ''', [cutoff_date, batch_size])
                
                batch_deleted = cursor.rowcount
                total_deleted += batch_deleted
                batch_num += 1
                
                if batch_deleted == 0:
                    break
                
                # 显示进度
                self.stdout.write(f'批次 {batch_num}: 删除 {batch_deleted:,} 条记录 (总计: {total_deleted:,})')
                
                # 提交事务
                connection.commit()
                
                # 短暂休息，避免数据库压力过大
                time.sleep(0.1)
        
        return total_deleted