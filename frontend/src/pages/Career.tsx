import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { careerStages, listCareerReports, listSavedJobs, removeSavedJob, saveCareerJob, type CareerReport, type CareerStage, type SavedJob } from '@/api/career';
import { getErrorMessage } from '@/api/errors';
import CareerReportView from '@/components/CareerReportView';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { Bookmark, Target } from 'lucide-react';

function SavedCard({ item, onUpdate, onRemove, onError, onNotice }: {
  item: SavedJob; onUpdate: (saved: SavedJob) => void; onRemove: () => void;
  onError: (message: string) => void; onNotice: (message: string) => void;
}) {
  const [stage, setStage] = useState(item.stage);
  const [notes, setNotes] = useState(item.notes);
  const [busy, setBusy] = useState(false);
  return <Card><CardContent className="pt-5 space-y-4">
    <div className="flex flex-wrap gap-2 justify-between"><div><Link to={`/opportunities/${item.job.id}`} className="font-semibold hover:underline">{item.job.title}</Link><p className="text-sm text-muted-foreground">{item.job.company}</p></div><Badge variant="outline">{item.job.status === 'ACTIVE' ? '招聘中' : '已停止招聘'}</Badge></div>
    <label className="flex flex-col gap-2 text-sm">求职进度<select aria-label={`${item.job.title} 求职进度`} className="rounded-md border bg-background px-3 h-10" value={stage} onChange={(e) => setStage(e.target.value as CareerStage)}>{Object.entries(careerStages).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
    <label className="flex flex-col gap-2 text-sm">个人备注<textarea aria-label={`${item.job.title} 个人备注`} placeholder="记录投递日期、面试安排或准备事项…" maxLength={4000} value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} className="w-full rounded-md border bg-background p-3 text-sm resize-y" /></label>
    <div className="flex flex-wrap gap-2">
      <Button size="sm" disabled={busy} onClick={async () => {
        setBusy(true); onError('');
        try { onUpdate(await saveCareerJob(item.job.id, stage, notes)); onNotice('求职进度已保存。'); }
        catch (err) { onError(getErrorMessage(err, '保存失败')); }
        finally { setBusy(false); }
      }}>{busy ? '正在保存…' : '保存进度'}</Button>
      <Link to={`/opportunities/${item.job.id}`}><Button size="sm" variant="outline">查看岗位与匹配度</Button></Link>
      <Button size="sm" variant="ghost" disabled={busy} onClick={async () => {
        setBusy(true); onError('');
        try { await removeSavedJob(item.job.id); onRemove(); onNotice('已移出我的求职，已有匹配报告仍保留。'); }
        catch (err) { onError(getErrorMessage(err, '移除失败')); }
        finally { setBusy(false); }
      }}>移除记录</Button>
    </div>
  </CardContent></Card>;
}

export default function Career() {
  const [params, setParams] = useSearchParams();
  const tab = params.get('tab') === 'reports' ? 'reports' : 'saved';
  const [saved, setSaved] = useState<SavedJob[]>([]);
  const [reports, setReports] = useState<CareerReport[]>([]);
  const [stageFilter, setStageFilter] = useState('');
  const [sort, setSort] = useState('date');
  const [selected, setSelected] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    let active = true;
    Promise.all([listSavedJobs(), listCareerReports()])
      .then(([bookmarks, history]) => { if (active) { setSaved(bookmarks); setReports(history); } })
      .catch((err) => { if (active) setError(getErrorMessage(err, '加载求职记录失败')); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const selectedReport = reports.find((r) => r.id === selected);
  const sortedReports = [...reports].sort((a, b) => sort === 'score'
    ? (b.overall_score ?? -1) - (a.overall_score ?? -1)
    : new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return <div className="flex flex-col gap-5">
    <div className="flex flex-wrap justify-between gap-3"><div><h2 className="text-2xl font-bold">我的求职</h2><p className="mt-1 text-sm text-muted-foreground">把目标岗位、准备计划和匹配报告放在一起。</p></div><Link to="/opportunities"><Button>探索更多岗位</Button></Link></div>
    <div className="grid gap-3 sm:grid-cols-3">{[
      ['关注岗位', saved.length], ['面试中', saved.filter((s) => s.stage === 'INTERVIEW').length], ['完成匹配', reports.filter((r) => r.status === 'COMPLETED').length],
    ].map(([label, count]) => <Card key={label}><CardContent className="pt-5"><p className="text-sm text-muted-foreground">{label}</p><p className="text-3xl font-bold mt-1">{count}</p></CardContent></Card>)}</div>
    <div className="flex flex-wrap gap-2" aria-label="求职记录分类"><Button variant={tab === 'saved' ? 'default' : 'outline'} onClick={() => setParams({ tab: 'saved' })}><Bookmark data-icon="inline-start" />收藏与进度</Button><Button variant={tab === 'reports' ? 'default' : 'outline'} onClick={() => setParams({ tab: 'reports' })}><Target data-icon="inline-start" />匹配报告</Button></div>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    {notice && <p role="status" className="text-sm text-primary">{notice}</p>}
    {loading ? <Spinner className="size-8 self-center my-8" /> : tab === 'saved' ? <>
      <p className="text-xs text-muted-foreground">进度由你手动记录。前往招聘原网页投递后，可在这里更新；本软件不会代你发送简历。</p>
      <select aria-label="筛选求职进度" className="self-start rounded-md border bg-background px-3 h-10 text-sm" value={stageFilter} onChange={(e) => setStageFilter(e.target.value)}><option value="">全部进度</option>{Object.entries(careerStages).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
      {!saved.filter((s) => !stageFilter || s.stage === stageFilter).length && <p className="py-8 text-muted-foreground text-center">暂无记录，去岗位探索收藏感兴趣的职位吧。</p>}
      <div className="grid gap-4 xl:grid-cols-2">{saved.filter((s) => !stageFilter || s.stage === stageFilter).map((item) => <SavedCard key={item.job.id} item={item} onUpdate={(row) => setSaved((prev) => prev.map((p) => p.job.id === row.job.id ? row : p))} onRemove={() => setSaved((prev) => prev.filter((p) => p.job.id !== item.job.id))} onError={setError} onNotice={setNotice} />)}</div>
    </> : <>
      <select aria-label="匹配报告排序" className="self-start rounded-md border bg-background px-3 h-10 text-sm" value={sort} onChange={(e) => setSort(e.target.value)}><option value="date">最近分析优先</option><option value="score">匹配度从高到低</option></select>
      {!reports.length && <p className="py-8 text-muted-foreground text-center">暂无匹配报告，打开岗位并选择自己的简历开始分析。</p>}
      <div className="flex flex-col gap-3">{sortedReports.map((r) => <Card key={r.id}><CardContent className="pt-4 pb-4 flex flex-wrap gap-3 items-center justify-between">
        <div><p className="font-medium">{r.job_title} · {r.company}</p><p className="text-xs text-muted-foreground mt-1">{r.resume_title} · {new Date(r.created_at).toLocaleString('zh-CN')}</p></div>
        <div className="flex gap-3 items-center"><Badge variant={r.status === 'COMPLETED' ? 'secondary' : 'outline'}>{r.status === 'COMPLETED' ? `匹配度 ${r.overall_score?.toFixed(0)} / 100` : r.status === 'FAILED' ? '分析失败' : '分析中'}</Badge><Button size="sm" variant="outline" onClick={() => setSelected(r.id)}>查看报告</Button></div>
      </CardContent></Card>)}</div>
      {selectedReport && <CareerReportView report={selectedReport} />}
    </>}
  </div>;
}
