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

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        
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
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] 将清理 {count} 个 {desc}')
            )
        else:
            if count > 0:
                deleted_count, _ = queryset.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'成功清理 {deleted_count} 个 {desc}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'没有找到需要清理的 {desc}')
                )
        
        # 显示统计信息
        total_count = Session.objects.count()
        expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
        self.stdout.write(f'当前总 sessions: {total_count}')
        self.stdout.write(f'当前过期 sessions: {expired_count}')