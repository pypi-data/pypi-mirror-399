from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = '清理过期的 Django sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示会清理多少过期 sessions，不实际删除',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='清理指定天数前的过期 sessions（默认只清理已过期的）',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，不询问确认',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        force = options['force']
        
        # 构建查询条件
        if days > 0:
            # 清理指定天数前的 sessions
            cutoff_date = timezone.now() - datetime.timedelta(days=days)
            queryset = Session.objects.filter(expire_date__lt=cutoff_date)
            desc = f'{days} 天前的 sessions'
        else:
            # 只清理已过期的 sessions
            queryset = Session.objects.filter(expire_date__lt=timezone.now())
            desc = '过期的 sessions'
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'没有找到需要清理的 {desc}')
            )
            return
        
        # 显示清理计划
        self.stdout.write(f'=== Sessions 清理计划 ===')
        self.stdout.write(f'清理目标: {desc}')
        self.stdout.write(f'将删除记录数: {count:,}')
        
        if not dry_run and not force:
            confirm = input('\n确认执行清理？(y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('清理操作已取消')
                return
        
        # 执行清理
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] 将清理 {count} 个 {desc}')
            )
        else:
            deleted_count, _ = queryset.delete()
            self.stdout.write(
                self.style.SUCCESS(f'成功清理 {deleted_count} 个 {desc}')
            )
        
        # 显示统计信息
        total_count = Session.objects.count()
        expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
        self.stdout.write(f'\n=== 当前状态 ===')
        self.stdout.write(f'当前总 sessions: {total_count:,}')
        self.stdout.write(f'当前过期 sessions: {expired_count:,}')
        
        if expired_count > 10000:
            self.stdout.write(
                self.style.WARNING(f'⚠️ 过期 sessions 数量较多，建议定期清理')
            )