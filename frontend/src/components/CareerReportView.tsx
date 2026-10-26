import type { CareerReport } from '@/api/career';
import ScoreCard from './ScoreCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function CareerReportView({ report }: { report: CareerReport }) {
  if (report.status === 'PENDING') return <p role="status" className="text-muted-foreground">分析正在进行中，请稍后刷新查看报告。</p>;
  if (report.status !== 'COMPLETED') return <p role="alert" className="text-destructive">
    {report.result_data?.error || '分析尚未完成，请稍后重试。'}
  </p>;
  const match = report.result_data?.match_result;
  const advice = report.result_data?.report;
  return <section className="flex flex-col gap-5" aria-label="岗位匹配报告">
    <div>
      <h3 className="text-xl font-semibold">你的岗位匹配报告</h3>
      <p className="mt-1 text-sm text-muted-foreground">{report.job_title} · {report.company} · 简历：{report.resume_title}</p>
      <p className="text-xs text-muted-foreground">{new Date(report.created_at).toLocaleString('zh-CN')} · 分数表示简历与岗位要求的匹配程度，不代表录用概率。</p>
    </div>
    <div className="grid gap-3 sm:grid-cols-3">
      <ScoreCard score={report.overall_score ?? 0} label="综合匹配度" size="md" />
      <ScoreCard score={match?.skill_match_score ?? 0} label="技能匹配度" size="md" />
      <ScoreCard score={match?.experience_match_score ?? 0} label="经验匹配度" size="md" />
    </div>
    <Card><CardContent className="pt-5 text-sm whitespace-pre-wrap">{advice?.summary || '暂无综合建议'}</CardContent></Card>
    <div className="grid gap-4 lg:grid-cols-2">
      <Card><CardHeader><CardTitle>已有优势</CardTitle></CardHeader><CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">{match?.matched_skills?.map((skill) => <Badge key={skill} variant="secondary">{skill}</Badge>)}</div>
        <p className="text-sm whitespace-pre-wrap">{match?.strengths_analysis}</p>
      </CardContent></Card>
      <Card><CardHeader><CardTitle>优先补齐的差距</CardTitle></CardHeader><CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">{match?.missing_skills?.map((skill) => <Badge key={skill} variant="outline">{skill}</Badge>)}</div>
        <p className="text-sm whitespace-pre-wrap">{match?.gap_analysis}</p>
      </CardContent></Card>
    </div>
    {[
      { title: '针对这个岗位修改简历', items: advice?.resume_tips },
      { title: '技能提升计划', items: advice?.learning_plan },
      { title: '面试准备清单', items: advice?.interview_preparation },
    ].map(({ title, items }) => <Card key={title}>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent><ol className="list-decimal pl-5 space-y-3 text-sm">{items?.map((item, i) => <li key={i} className="whitespace-pre-wrap">{item}</li>)}</ol></CardContent>
    </Card>)}
  </section>;
}
