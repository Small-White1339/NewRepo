import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { createJob, listJobs, updateJob, deleteJob } from '../api/jobs';
import StatusBadge from '../components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell
} from '@/components/ui/table';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger } from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
} from '@/components/ui/alert-dialog';
import { Briefcase, Plus, Trash2, Pencil } from 'lucide-react';
import type { JobListItem, JobLevel, JobStatus } from '../types';

const JOB_LEVELS: Record<JobLevel, string> = {
  JUNIOR: '初级',
  INTERMEDIATE: '中级',
  SENIOR: '高级',
  EXPERT: '专家',
};

const STATUS_LABELS: Record<string, string> = {
  DRAFT: '草稿',
  ACTIVE: '发布中',
  CLOSED: '已关闭',
};

export default function Jobs() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [level, setLevel] = useState<JobLevel>('INTERMEDIATE');
  const [description, setDescription] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<JobListItem | null>(null);
  const [editingJob, setEditingJob] = useState<JobListItem | null>(null);
  const [editForm, setEditForm] = useState({ title: '', company: '', level: '', status: '', raw_description: '' });

  const fetchJobs = async () => {
    try {
      const params: { q?: string } = {};
      if (searchQuery) params.q = searchQuery;
      const data = await listJobs(params);
      setJobs(data);
    } catch {
      setError('加载岗位列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [searchQuery]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await createJob({ title, company, level, raw_description: description });
      setTitle('');
      setCompany('');
      setLevel('INTERMEDIATE');
      setDescription('');
      setShowForm(false);
      await fetchJobs();
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response: { data?: { detail?: string } } }).response?.data?.detail || '创建失败'
          : '创建失败';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };
  const handleEditSubmit = async () => {
    if (!editingJob) return;
    try {
      await updateJob(editingJob.id, { title: editForm.title, company: editForm.company, level: editForm.level as JobLevel, status: editForm.status as JobStatus });
      setEditingJob(null);
      await fetchJobs();
    } catch {
      setError('更新失败');
    }
  };
  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteJob(deleteTarget.id);
      setDeleteTarget(null);
      await fetchJobs();
    } catch {
      setError('删除失败');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">岗位管理</h2>
        <div className="flex gap-2">
          <Input
            placeholder="搜索岗位..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48"
          />
          <Button
            variant={showForm ? 'outline' : 'default'}
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? '取消' : <><Plus data-icon="inline-start" />创建岗位</>}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Create Job Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>新建岗位</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="flex flex-col gap-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <label htmlFor="job-title" className="text-sm font-medium">岗位名称</label>
                  <Input
                    id="job-title"
                    type="text"
                    placeholder="例：高级前端工程师"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label htmlFor="job-company" className="text-sm font-medium">公司名称</label>
                  <Input
                    id="job-company"
                    type="text"
                    placeholder="例：某某科技有限公司"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium">岗位职级</label>
                <Select value={level} onValueChange={(v) => setLevel(v as JobLevel)}>
                  <SelectTrigger className="w-full sm:w-48">
                    {JOB_LEVELS[level] || level}
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      {(Object.entries(JOB_LEVELS) as [JobLevel, string][]).map(([key, label]) => (
                        <SelectItem key={key} value={key}>{label}</SelectItem>
                      ))}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex flex-col gap-2">
                <label htmlFor="job-desc" className="text-sm font-medium">岗位描述 (JD)</label>
                <Textarea
                  id="job-desc"
                  placeholder="请输入完整的岗位描述文本..."
                  className="min-h-32"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                />
              </div>
              <div>
                <Button type="submit" disabled={submitting}>
                  {submitting && <Spinner data-icon="inline-start" />}
                  {submitting ? '创建中...' : '创建并保存'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Job List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner className="size-8 text-primary" />
        </div>
      ) : jobs.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center text-center py-12">
            <Briefcase className="size-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground">暂无岗位</h3>
            <p className="text-sm text-muted-foreground/60 mt-1">点击"创建岗位"开始添加岗位信息</p>
          </CardContent>
        </Card>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>岗位名称</TableHead>
              <TableHead>公司</TableHead>
              <TableHead>职级</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead>操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell className="font-medium">{job.title}</TableCell>
                <TableCell className="text-muted-foreground">{job.company}</TableCell>
                <TableCell>
                  <span className="text-sm text-muted-foreground">{JOB_LEVELS[job.level] || job.level}</span>
                </TableCell>
                <TableCell><StatusBadge status={job.status} /></TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(job.created_at).toLocaleString('zh-CN')}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Link to={`/jobs/${job.id}`}>
                      <Button variant="ghost" size="sm">详情</Button>
                    </Link>
                    <Button
                      variant="ghost" size="sm"
                      onClick={async () => {
                        setEditForm({ title: job.title, company: job.company, level: job.level, status: job.status, raw_description: '' });
                        setEditingJob(job);
                        try {
                          const { getJob } = await import('../api/jobs');
                          const detail = await getJob(job.id);
                          setEditForm({ title: detail.title, company: detail.company, level: detail.level, status: detail.status, raw_description: detail.raw_description || '' });
                        } catch {}
                      }}
                    >
                      <Pencil className="size-4" />
                    </Button>
                    <Button
                      variant="ghost" size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(job)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editingJob} onOpenChange={(o) => !o && setEditingJob(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑岗位</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4 py-2">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">岗位名称</label>
              <Input value={editForm.title} onChange={(e) => setEditForm({...editForm, title: e.target.value})} />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">公司</label>
              <Input value={editForm.company} onChange={(e) => setEditForm({...editForm, company: e.target.value})} />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">职级</label>
              <Select value={editForm.level} onValueChange={(v) => v && setEditForm({...editForm, level: v})}>
                <SelectTrigger><span>{JOB_LEVELS[editForm.level as JobLevel] || editForm.level}</span></SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {(Object.entries(JOB_LEVELS) as [string, string][]).map(([k, l]) => (
                      <SelectItem key={k} value={k}>{l}</SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">状态</label>
              <Select value={editForm.status} onValueChange={(v) => v && setEditForm({...editForm, status: v})}>
                <SelectTrigger><span>{STATUS_LABELS[editForm.status] || editForm.status}</span></SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="DRAFT">草稿</SelectItem>
                    <SelectItem value="ACTIVE">发布中</SelectItem>
                    <SelectItem value="CLOSED">已关闭</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">岗位描述 (JD)</label>
              <Textarea
                value={editForm.raw_description}
                onChange={(e) => setEditForm({...editForm, raw_description: e.target.value})}
                className="h-24 resize-none"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingJob(null)}>取消</Button>
            <Button onClick={handleEditSubmit}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除岗位</AlertDialogTitle>
            <AlertDialogDescription>
              确认删除「{deleteTarget?.title}」？<br />
              关联的匹配分析报告也将同步删除，此操作不可撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeleteTarget(null)}>取消</AlertDialogCancel>
            <Button variant="destructive" onClick={handleDelete}>确认删除</Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
