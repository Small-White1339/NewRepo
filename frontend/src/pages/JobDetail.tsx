import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getJob, analyzeJob, deleteJob } from '../api/jobs';
import StatusBadge from '../components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
} from '@/components/ui/alert-dialog';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell
} from '@/components/ui/table';
import { ArrowLeft, Sparkles, Trash2 } from 'lucide-react';
import type { JobResponse } from '../types';

const JOB_LEVEL_LABELS: Record<string, string> = {
  JUNIOR: '初级',
  INTERMEDIATE: '中级',
  SENIOR: '高级',
  EXPERT: '专家',
};

export default function JobDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [error, setError] = useState('');

  const fetchJob = async () => {
    if (!id) return;
    try {
      const data = await getJob(id);
      setJob(data);
    } catch {
      setError('加载岗位详情失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
  }, [id]);

  const handleAnalyze = async () => {
    if (!id) return;
    setAnalyzing(true);
    try {
      await analyzeJob(id);
      await fetchJob();
    } catch {
      setError('AI 分析失败');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner className="size-8 text-primary" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error || '岗位不存在'}
        </div>
        <Link to="/jobs"><Button variant="ghost">返回列表</Button></Link>
      </div>
    );
  }

  const structured = job.structured_data;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/jobs">
            <Button variant="ghost" size="sm">
              <ArrowLeft data-icon="inline-start" /> 返回
            </Button>
          </Link>
          <h2 className="text-2xl font-bold text-foreground">岗位详情</h2>
          <StatusBadge status={job.status} />
        </div>
        <div className="flex gap-2">
          <Button disabled={analyzing} onClick={handleAnalyze}>
            {analyzing ? <><Spinner data-icon="inline-start" />分析中...</> : <><Sparkles data-icon="inline-start" />AI 分析 JD</>}
          </Button>
          <Button
            variant="outline" size="sm"
            className="text-destructive border-destructive/30"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="size-4" /> 删除
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>基本信息</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm">
            <p><span className="font-medium">岗位名称：</span>{job.title}</p>
            <p><span className="font-medium">公司：</span>{job.company}</p>
            <p><span className="font-medium">职级：</span>{JOB_LEVEL_LABELS[job.level] || job.level}</p>
            <p><span className="font-medium">状态：</span>
              <span className={job.status === 'ACTIVE' ? 'text-emerald-600 font-medium' : job.status === 'CLOSED' ? 'text-muted-foreground' : ''}>
                {{ DRAFT: '草稿', ACTIVE: '发布中', CLOSED: '已关闭' }[job.status] || job.status}
              </span>
            </p>
            <p><span className="font-medium">创建时间：</span>{new Date(job.created_at).toLocaleString('zh-CN')}</p>
          </CardContent>
        </Card>

        {/* AI Analysis Results */}
        {structured && (
          <Card>
            <CardHeader>
              <CardTitle className="text-primary">AI 分析结果</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm">
              <p><span className="font-medium">岗位名称：</span>{(structured as { job_title?: string }).job_title || '—'}</p>
              <p><span className="font-medium">学历要求：</span>{(structured as { education_requirement?: string }).education_requirement || '—'}</p>
              <p><span className="font-medium">经验要求：</span>{(structured as { experience_requirement?: string }).experience_requirement || '—'}</p>

              {(structured as { mandatory_requirements?: string[] }).mandatory_requirements?.length ? (
                <div className="mt-2">
                  <p className="font-medium mb-1">硬性要求：</p>
                  <ul className="list-disc list-inside text-muted-foreground">
                    {(structured as { mandatory_requirements: string[] }).mandatory_requirements.map((req, i) => (
                      <li key={i}>{req}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {(structured as { nice_to_have?: string[] }).nice_to_have?.length ? (
                <div className="mt-2">
                  <p className="font-medium mb-1">加分项：</p>
                  <ul className="list-disc list-inside text-muted-foreground">
                    {(structured as { nice_to_have: string[] }).nice_to_have.map((nth, i) => (
                      <li key={i}>{nth}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </CardContent>
          </Card>
        )}

        {/* Required Skills */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>技能要求</CardTitle>
          </CardHeader>
          <CardContent>
            {job.requirements.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无结构化技能要求，点击"AI 分析 JD"自动提取</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>技能</TableHead>
                    <TableHead>类别</TableHead>
                    <TableHead>重要性</TableHead>
                    <TableHead>硬性要求</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {job.requirements.map((req) => (
                    <TableRow key={req.id}>
                      <TableCell className="font-medium">{req.name}</TableCell>
                      <TableCell>{req.category}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-20 rounded-full bg-muted overflow-hidden">
                            <div
                              className="h-full rounded-full bg-primary"
                              style={{ width: `${req.importance * 10}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">{req.importance}/10</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {req.is_mandatory ? (
                          <Badge variant="destructive" className="text-xs">必需</Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">可选</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Raw Description */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>原始岗位描述</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm whitespace-pre-wrap font-sans text-muted-foreground max-h-80 overflow-y-auto bg-muted/50 rounded-lg p-4">
              {job.raw_description || '暂无描述'}
            </pre>
          </CardContent>
        </Card>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除岗位</AlertDialogTitle>
            <AlertDialogDescription>
              确认删除「{job?.title}」？<br />
              关联的匹配分析报告也将同步删除，此操作不可撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowDeleteDialog(false)}>取消</AlertDialogCancel>
            <Button variant="destructive" onClick={async () => {
              if (!job) return;
              try { await deleteJob(job.id); navigate('/jobs'); }
              catch { setError('删除失败'); }
              finally { setShowDeleteDialog(false); }
            }}>确认删除</Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
