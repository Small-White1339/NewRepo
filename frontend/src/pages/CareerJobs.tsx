import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { browseCareerJobs, listSavedJobs, saveCareerJob, type CareerJob } from '@/api/career';
import { getErrorMessage } from '@/api/errors';
import SourceInfo from '@/components/SourceInfo';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { Bookmark, Briefcase, ArrowUpRight, Search } from 'lucide-react';

const levels: Record<string, string> = { JUNIOR: '初级', INTERMEDIATE: '中级', SENIOR: '高级', EXPERT: '专家', UNSPECIFIED: '以原文为准' };

export default function CareerJobs() {
  const [jobs, setJobs] = useState<CareerJob[]>([]);
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState('');
  const [level, setLevel] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    const timer = setTimeout(() => {
      Promise.all([browseCareerJobs({ q: query, level: level || undefined }), listSavedJobs()])
        .then(([rows, bookmarks]) => { if (active) { setJobs(rows); setSaved(new Set(bookmarks.map((b) => b.job.id))); } })
        .catch((err) => { if (active) setError(getErrorMessage(err, '岗位加载失败，请重试')); })
        .finally(() => { if (active) setLoading(false); });
    }, 250);
    return () => { active = false; clearTimeout(timer); };
  }, [query, level]);

  return <div className="flex flex-col gap-5">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><h2 className="text-2xl font-bold">岗位探索</h2><p className="mt-1 text-sm text-muted-foreground">从真实岗位出发，了解自己与目标岗位的距离。</p></div>
      <Link to="/career"><Button variant="outline"><Bookmark data-icon="inline-start" />我的求职</Button></Link>
    </div>
    <Card><CardContent className="pt-5 space-y-3">
      <div className="flex flex-wrap gap-3 items-center">
        <label className="relative flex-1 min-w-48"><Search className="absolute left-3 top-3 size-4 text-muted-foreground" /><Input aria-label="搜索岗位" placeholder="岗位、公司、技能或城市，例如 Python、London" className="pl-9" value={query} onChange={(e) => setQuery(e.target.value)} /></label>
        <select aria-label="筛选岗位职级" value={level} onChange={(e) => setLevel(e.target.value)} className="h-10 rounded-md border bg-background px-3 text-sm">
          <option value="">全部职级</option>{Object.entries(levels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
        </select>
      </div>
      <p className="text-xs text-muted-foreground">公开招聘信息会随时间变化，请在原始招聘页面确认地点、要求及是否仍可投递。你的简历只用于自己的分析。</p>
    </CardContent></Card>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    {notice && <p role="status" className="text-sm text-primary">{notice}</p>}
    {loading ? <Spinner className="size-8 self-center my-8" /> : <>
      <p className="text-sm text-muted-foreground">找到 {jobs.length} 个在招岗位</p>
      {!jobs.length && !error && <Card><CardContent className="py-10 text-center text-muted-foreground">暂无符合条件的岗位，请尝试其他关键词或等待 HR 发布岗位。</CardContent></Card>}
      <div className="grid gap-4 xl:grid-cols-2">{jobs.map((job) => <Card key={job.id}>
        <CardContent className="pt-5 flex flex-col gap-3 h-full">
          <div className="flex gap-3 items-start"><Briefcase className="size-5 mt-1 shrink-0 text-primary" /><div className="min-w-0"><Link to={`/opportunities/${job.id}`} className="font-semibold hover:underline break-words">{job.title}</Link><p className="text-sm text-muted-foreground">{job.company}</p></div></div>
          <div><Badge variant="secondary">{levels[job.level] || job.level}</Badge><SourceInfo name={job.source_name} url={job.source_url} importedAt={job.imported_at} /></div>
          <p className="line-clamp-3 text-sm text-muted-foreground whitespace-pre-wrap">{job.raw_description?.slice(0, 260)}{(job.raw_description?.length || 0) > 260 ? '…' : ''}</p>
          <div className="flex flex-wrap gap-2 mt-auto pt-1">
            <Link to={`/opportunities/${job.id}`}><Button size="sm">查看岗位与匹配度<ArrowUpRight data-icon="inline-end" /></Button></Link>
            <Button size="sm" variant="outline" disabled={saved.has(job.id) || saving === job.id} onClick={async () => {
              setSaving(job.id); setError('');
              try { await saveCareerJob(job.id); setSaved((prev) => new Set([...prev, job.id])); setNotice(`已收藏「${job.title}」，可在“我的求职”中记录进度。`); }
              catch (err) { setError(getErrorMessage(err, '收藏失败')); }
              finally { setSaving(''); }
            }}><Bookmark data-icon="inline-start" />{saved.has(job.id) ? '已收藏' : '收藏岗位'}</Button>
          </div>
        </CardContent>
      </Card>)}</div>
    </>}
  </div>;
}
