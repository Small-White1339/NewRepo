import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMatch } from '../api/matches';
import ScoreCard from '../components/ScoreCard';
import StatusBadge from '../components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { ArrowLeft } from 'lucide-react';
import type { MatchReportResponse, MatchResultData, ReportResult, MatchAnalysisResult } from '../types';

function getHiringBadge(recommendation?: string) {
  const config: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }> = {
    strong_hire: { variant: 'default', label: '强烈推荐录用' },
    hire: { variant: 'default', label: '推荐录用' },
    consider: { variant: 'secondary', label: '可考虑' },
    weak: { variant: 'destructive', label: '不推荐' },
    not_recommended: { variant: 'destructive', label: '不建议录用' },
  };
  return config[recommendation || ''] || { variant: 'outline' as const, label: '未评估' };
}

export default function MatchDetail() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<MatchReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    getMatch(id)
      .then(setReport)
      .catch(() => setError('加载报告失败'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner className="size-8 text-primary" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error || '报告不存在'}
        </div>
        <Link to="/matches"><Button variant="ghost">返回列表</Button></Link>
      </div>
    );
  }

  if (report.status === 'PENDING') {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <Spinner className="size-8 text-primary" />
        <p className="text-muted-foreground">分析进行中，请稍候...</p>
        <Link to="/matches"><Button variant="ghost">返回列表</Button></Link>
      </div>
    );
  }

  if (report.status === 'FAILED') {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          分析失败：{(report.result_data as { error?: string })?.error || '未知错误'}
        </div>
        <Link to="/matches"><Button variant="ghost">返回列表</Button></Link>
      </div>
    );
  }

  const result = report.result_data as MatchResultData | undefined;
  const matchResult = result?.match_result as MatchAnalysisResult | undefined;
  const reportData = result?.report as ReportResult | undefined;
  const badge = getHiringBadge(reportData?.hiring_recommendation);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Link to="/matches">
          <Button variant="ghost" size="sm">
            <ArrowLeft data-icon="inline-start" /> 返回
          </Button>
        </Link>
        <h2 className="text-2xl font-bold text-foreground">匹配分析报告</h2>
        <StatusBadge status={report.status} />
      </div>

      {/* Overall Score & Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-1">
          <ScoreCard score={report.overall_score || 0} label="综合匹配度" size="lg" />
        </div>
        <div className="lg:col-span-1">
          <ScoreCard score={matchResult?.skill_match_score ?? 0} label="技能匹配" size="md" />
        </div>
        <div className="lg:col-span-1">
          <ScoreCard score={matchResult?.experience_match_score ?? 0} label="经验匹配" size="md" />
        </div>
        <div className="lg:col-span-1 flex flex-col items-center justify-center rounded-xl border bg-card p-4">
          <span className="text-sm text-muted-foreground mb-2">招聘建议</span>
          <Badge variant={badge.variant} className="text-sm px-3 py-1">{badge.label}</Badge>
        </div>
      </div>

      {/* Skills Match */}
      <Card>
        <CardHeader>
          <CardTitle>技能匹配详情</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-emerald-600 mb-2">
                匹配技能 ({matchResult?.matched_skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-2">
                {matchResult?.matched_skills?.map((s, i) => (
                  <Badge key={i} variant="outline" className="border-emerald-500 text-emerald-700 bg-emerald-50 dark:bg-emerald-950/20 dark:text-emerald-400">{s}</Badge>
                )) || <span className="text-sm text-muted-foreground">无</span>}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-destructive mb-2">
                缺失技能 ({matchResult?.missing_skills?.length || 0})
              </p>
              <div className="flex flex-wrap gap-2">
                {matchResult?.missing_skills?.map((s, i) => (
                  <Badge key={i} variant="outline" className="border-destructive/50 text-destructive bg-destructive/5">{s}</Badge>
                )) || <span className="text-sm text-muted-foreground">无</span>}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-emerald-600">优势分析</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{matchResult?.strengths_analysis || '暂无分析'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-amber-500">差距分析</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{matchResult?.gap_analysis || '暂无分析'}</p>
          </CardContent>
        </Card>
      </div>

      {/* Executive Summary */}
      {reportData?.executive_summary && (
        <Card>
          <CardHeader>
            <CardTitle>综合摘要</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{reportData.executive_summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Interview Suggestions */}
      {reportData?.interview_suggestions && reportData.interview_suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sky-600">面试建议</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside text-sm flex flex-col gap-1">
              {reportData.interview_suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Follow-up Questions */}
      {reportData?.follow_up_questions && reportData.follow_up_questions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>追问建议</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside text-sm flex flex-col gap-1">
              {reportData.follow_up_questions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Strengths & Weaknesses from Resume Analysis */}
      {result?.resume_analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {result.resume_analysis.strengths?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-emerald-600">简历优势</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside text-sm flex flex-col gap-1">
                  {result.resume_analysis.strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
          {result.resume_analysis.weaknesses?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-destructive">简历不足</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside text-sm flex flex-col gap-1">
                  {result.resume_analysis.weaknesses.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
