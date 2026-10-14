import { Badge } from '@/components/ui/badge';
import type { ResumeStatus, JobStatus, MatchStatus } from '../types';

interface StatusBadgeProps {
  status: ResumeStatus | JobStatus | MatchStatus;
}

const statusConfig: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost'; label: string }> = {
  PENDING: { variant: 'secondary', label: '待处理' },
  PARSED: { variant: 'default', label: '已解析' },
  FAILED: { variant: 'destructive', label: '失败' },
  ACTIVE: { variant: 'default', label: '发布中' },
  CLOSED: { variant: 'outline', label: '已关闭' },
  ARCHIVED: { variant: 'ghost', label: '已归档' },
  COMPLETED: { variant: 'default', label: '已完成' },
  DRAFT: { variant: 'secondary', label: '草稿' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] ?? { variant: 'outline' as const, label: status };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
