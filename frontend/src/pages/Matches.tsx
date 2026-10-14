import { useEffect, useState, useRef, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { listMatches, analyzeMatch } from '../api/matches';
import { listResumes } from '../api/resumes';
import { listJobs } from '../api/jobs';
import StatusBadge from '../components/StatusBadge';
import { Button } from '@/components/ui/button';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell
} from '@/components/ui/table';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
  Select, SelectContent, SelectGroup, SelectItem, SelectTrigger
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Spinner } from '@/components/ui/spinner';
import { Target, Zap, ChevronDown } from 'lucide-react';
import type { MatchReportListItem, ResumeListItem, JobListItem } from '../types';

const LEVEL_LABELS: Record<string, string> = { JUNIOR: '初级', INTERMEDIATE: '中级', SENIOR: '高级', EXPERT: '专家' };

export default function Matches() {
  const { isHR } = useAuth();
  const [matches, setMatches] = useState<MatchReportListItem[]>([]);
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedResumeIds, setSelectedResumeIds] = useState<string[]>([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [resumeOpen, setResumeOpen] = useState(false);
  const [resumeSearch, setResumeSearch] = useState('');

  const filteredResumes = resumes
    .filter((r) => r.status === 'PARSED')
    .filter((r) => !resumeSearch || r.title.toLowerCase().includes(resumeSearch.toLowerCase()));

  const selectedJobLabel = selectedJob
    ? (() => { const j = jobs.find(j => j.id === selectedJob); return j ? `${j.title} [${LEVEL_LABELS[j.level] || j.level}] - ${j.company}` : '请选择岗位...'; })()
    : '请选择岗位...';

  const fetchData = async () => {
    try {
      const [m, r, j] = await Promise.all([
        listMatches(),
        listResumes(),
        listJobs(),
      ]);
      setMatches(m);
      setResumes(r);
      setJobs(j);
    } catch {
      setError('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAnalyze = async (e: FormEvent) => {
    e.preventDefault();
    if (selectedResumeIds.length === 0 || !selectedJob) return;
    setError('');
    setAnalyzing(true);
    try {
      await analyzeMatch({ resume_ids: selectedResumeIds, job_id: selectedJob });
      setSelectedResumeIds([]);
      setSelectedJob('');
      await fetchData();
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response: { data?: { detail?: string } } }).response?.data?.detail || '分析失败'
          : '分析失败';
      setError(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  const getScoreColor = (score?: number) => {
    if (score === undefined || score === null) return '';
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-amber-500';
    return 'text-destructive';
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">匹配分析</h2>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Analyze Form */}
      <Card>
        <CardHeader>
          <CardTitle>新建匹配分析</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAnalyze} className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex flex-col gap-2 flex-1 w-full">
              <label className="text-sm font-medium">选择简历（可多选）</label>
              <Popover open={resumeOpen} onOpenChange={(o) => { setResumeOpen(o); if (!o) setResumeSearch(''); }}>
                <PopoverTrigger className="flex w-full items-center justify-between rounded-lg border border-input bg-transparent px-3 py-2 text-sm whitespace-nowrap">
                  {selectedResumeIds.length > 0 ? `已选 ${selectedResumeIds.length} 份简历` : '请选择简历...'}
                  <ChevronDown className="size-4 shrink-0 opacity-50" />
                </PopoverTrigger>
                <PopoverContent className="p-2" align="start" style={{ width: 'var(--anchor-width)' }}>
                  <Input
                    placeholder="搜索简历..."
                    value={resumeSearch}
                    onChange={(e) => setResumeSearch(e.target.value)}
                    className="mb-2"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div className="flex flex-col gap-1 max-h-48 overflow-y-auto">
                    {filteredResumes.length === 0 ? (
                      <p className="text-sm text-muted-foreground px-2 py-4 text-center">
                        {resumeSearch ? '未找到匹配的简历' : '暂无可分析的简历'}
                      </p>
                    ) : (
                      filteredResumes.map((r) => (
                        <label key={r.id} className="flex items-center gap-2 cursor-pointer px-2 py-1.5 rounded text-sm hover:bg-accent">
                          <input
                            type="checkbox"
                            checked={selectedResumeIds.includes(r.id)}
                            onChange={() => {
                              setSelectedResumeIds((prev) =>
                                prev.includes(r.id) ? prev.filter((id) => id !== r.id) : [...prev, r.id]
                              );
                            }}
                            className="size-4 rounded border-gray-300"
                          />
                          <span className="truncate">{r.title}</span>
                        </label>
                      ))
                    )}
                  </div>
                </PopoverContent>
              </Popover>
            </div>
            <div className="flex flex-col gap-2 flex-1 w-full">
              <label className="text-sm font-medium">选择岗位</label>
              <Select value={selectedJob} onValueChange={(v) => v && setSelectedJob(v)}>
                <SelectTrigger className="w-full">
                  {selectedJobLabel}
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {jobs.map((j) => (
                      <SelectItem key={j.id} value={j.id}>{j.title} [{LEVEL_LABELS[j.level] || j.level}] - {j.company}</SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <Button
              type="submit"
              disabled={analyzing || selectedResumeIds.length === 0 || !selectedJob}
              className="w-full sm:w-auto"
            >
              {analyzing ? <><Spinner data-icon="inline-start" />分析中...</> : <><Zap data-icon="inline-start" />开始分析</>}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Match Results List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner className="size-8 text-primary" />
        </div>
      ) : matches.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center text-center py-12">
            <Target className="size-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground">暂无匹配分析</h3>
            <p className="text-sm text-muted-foreground/60 mt-1">选择一个简历和一个岗位，点击"开始分析"</p>
          </CardContent>
        </Card>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>简历</TableHead>
              <TableHead>岗位</TableHead>
              <TableHead>综合评分</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>分析时间</TableHead>
              <TableHead>操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {matches.map((m) => {
              const resume = resumes.find((r) => r.id === m.resume_id);
              const job = jobs.find((j) => j.id === m.job_id);
              return (
                <TableRow key={m.id}>
                  <TableCell className="font-medium">{resume?.title || m.resume_id.slice(0, 8)}</TableCell>
                  <TableCell>{job?.title || m.job_id.slice(0, 8)}</TableCell>
                  <TableCell>
                    {m.overall_score !== null && m.overall_score !== undefined ? (
                      <span className={`font-bold text-lg ${getScoreColor(m.overall_score)}`}>
                        {Math.round(m.overall_score)}
                      </span>
                    ) : (
                      <span className="text-muted-foreground/40">—</span>
                    )}
                  </TableCell>
                  <TableCell><StatusBadge status={m.status} /></TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(m.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell>
                    <Link to={`/matches/${m.id}`}>
                      <Button variant="ghost" size="sm">查看报告</Button>
                    </Link>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
