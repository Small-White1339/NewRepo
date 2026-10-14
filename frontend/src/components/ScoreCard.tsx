import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ScoreCardProps {
  score?: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-amber-500';
  return 'text-destructive';
}

function getScoreRing(score: number): string {
  if (score >= 80) return 'ring-emerald-500/30';
  if (score >= 60) return 'ring-amber-400/30';
  return 'ring-destructive/30';
}

export default function ScoreCard({ score = 0, label, size = 'md' }: ScoreCardProps) {
  const textSize = size === 'lg' ? 'text-4xl' : size === 'sm' ? 'text-xl' : 'text-2xl';

  return (
    <Card className={cn('text-center', getScoreRing(score))}>
      <CardContent className="flex flex-col items-center gap-1 pt-6 pb-4">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className={cn('font-bold', textSize, getScoreColor(score))}>
          {Math.round(score)}
          <span className="text-base font-normal text-muted-foreground">/100</span>
        </span>
      </CardContent>
    </Card>
  );
}
