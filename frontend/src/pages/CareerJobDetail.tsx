import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { analyzeCareerMatch, getCareerJob, listCareerReports, listSavedJobs, saveCareerJob, type CareerJob, type CareerReport } from '@/api/career';
import { listResumes } from '@/api/resumes';
import { getErrorMessage } from '@/api/errors';
import type { ResumeListItem } from '@/types';
import CareerReportView from '@/components/CareerReportView';
import SourceInfo from '@/components/SourceInfo';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { ArrowLeft, Bookmark, ExternalLink, Target } from 'lucide-react';

export default function CareerJobDetail() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<CareerJob | null>(null);
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumeId, setResumeId] = useState('');
  const [reports, setReports] = useState<CareerReport[]>([]);
  const [report, setReport] = useState<CareerReport | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    let active = true;
    setLoading(true); setError(''); setReport(null);
    Promise.all([getCareerJob(id), listResumes(), listSavedJobs(), listCareerReports()])
      .then(([row, files, bookmarks, history]) => {
        if (!active) return;
        setJob(row); setResumes(files); setResumeId(files[0]?.id || '');
        setSaved(bookmarks.some((b) => b.job.id === id));
        setReports(history.filter((r) => r.job_id === id));
      })
      .catch((err) => { if (active) setError(getErrorMessage(err, '加载岗位失败')); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);

  if (loading) return <Spinner className="size-8 mx-auto my-12" />;
  if (!job) return <div className="space-y-4"><p role="alert" className="text-destructive">{error || '岗位不存在'}</p><Link to="/opportunities"><Button variant="outline">返回岗位探索</Button></Link></div>;
  const selectedReports = reports.filter((r) => r.resume_id === resumeId);
  const visibleReport = report?.resume_id === resumeId ? report : selectedReports[0];
  const externalUrl = job.source_url && /^https?:\/\//i.test(job.source_url) ? job.source_url : null;

  return <div className="flex flex-col gap-6">
    <Link to="/opportunities" className="self-start"><Button variant="ghost" size="sm"><ArrowLeft data-icon="inline-start" />岗位探索</Button></Link>
    <div className="flex flex-wrap gap-4 justify-between">
      <div><h2 className="text-2xl font-bold break-words">{job.title}</h2><p className="mt-1 text-muted-foreground">{job.company} · {job.status === 'ACTIVE' ? '招聘中' : '已停止招聘'}</p><SourceInfo name={job.source_name} url={job.source_url} importedAt={job.imported_at} /></div>
      <div className="flex flex-wrap gap-2 items-start">
        <Button variant="outline" disabled={saved || saving || job.status !== 'ACTIVE'} onClick={async () => {
          setSaving(true); setError('');
          try { await saveCareerJob(job.id); setSaved(true); }
          catch (err) { setError(getErrorMessage(err, '收藏失败')); }
          finally { setSaving(false); }
        }}><Bookmark data-icon="inline-start" />{saved ? '已收藏' : '收藏岗位'}</Button>
        {externalUrl && <a href={externalUrl} target="_blank" rel="noopener noreferrer"><Button variant="secondary"><ExternalLink data-icon="inline-start" />前往原招聘页面</Button></a>}
      </div>
    </div>
    <Card><CardHeader><CardTitle>用我的简历测匹配度</CardTitle></CardHeader><CardContent className="space-y-4">
      <p className="text-sm text-muted-foreground">选择自己的简历，获取综合、技能、经验匹配分数，以及针对这个岗位的准备建议。分析时简历文本和岗位描述会发送至已配置的 AI 服务。</p>
      {resumes.length ? <div className="flex flex-wrap gap-3 items-center">
        <select aria-label="选择匹配简历" className="min-w-0 max-w-full rounded-md border bg-background px-3 h-10 text-sm" value={resumeId} disabled={analyzing} onChange={(e) => setResumeId(e.target.value)}>
          {resumes.map((resume) => <option value={resume.id} key={resume.id}>{resume.title}</option>)}
        </select>
        <Button disabled={analyzing || !resumeId || job.status !== 'ACTIVE'} onClick={async () => {
          setAnalyzing(true); setError(''); setReport(null);
          try {
            const result = await analyzeCareerMatch(job.id, resumeId);
            setReport(result); setReports((prev) => [result, ...prev]);
          } catch (err) { setError(getErrorMessage(err, '匹配分析失败，请重试')); }
          finally { setAnalyzing(false); }
        }}>{analyzing ? <Spinner data-icon="inline-start" /> : <Target data-icon="inline-start" />}{analyzing ? '正在分析，请稍候…' : selectedReports.length ? '重新分析匹配度' : '开始匹配分析'}</Button>
      </div> : <Link to="/resumes"><Button>先上传我的简历</Button></Link>}
      {analyzing && <p role="status" className="text-sm text-muted-foreground">正在分析简历、岗位要求和差距，通常需要一至数分钟。请保持页面打开。</p>}
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    </CardContent></Card>
    {visibleReport && <CareerReportView report={visibleReport} />}
    <Card><CardHeader><CardTitle>原始岗位说明</CardTitle></CardHeader><CardContent><p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{job.raw_description || '暂无详细说明，请查看原招聘页面。'}</p></CardContent></Card>
  </div>;
}
