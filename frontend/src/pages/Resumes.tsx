import { useEffect, useState, useRef, type ChangeEvent } from 'react';
import { Link } from 'react-router-dom';
import { listResumes, uploadResume, deleteResume } from '../api/resumes';
import StatusBadge from '../components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell
} from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
} from '@/components/ui/alert-dialog';
import { FileText, Upload, Trash2, Search, Eye, Download } from 'lucide-react';
import type { ResumeListItem } from '../types';

export default function Resumes() {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<ResumeListItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumes = async () => {
    try {
      const params: { q?: string } = {};
      if (searchQuery) params.q = searchQuery;
      const data = await listResumes(params);
      setResumes(data);
    } catch {
      setError('加载简历列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, [searchQuery]);

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await uploadResume(file);
      if (fileInputRef.current) fileInputRef.current.value = '';
      await fetchResumes();
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response: { data?: { detail?: string } } }).response?.data?.detail || '上传失败'
          : '上传失败';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteResume(deleteTarget.id);
      setDeleteTarget(null);
      await fetchResumes();
    } catch {
      setError('删除失败');
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">简历管理</h2>
        <div className="flex gap-2">
          <Input
            placeholder="搜索简历..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48"
          />
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button disabled={uploading} onClick={() => fileInputRef.current?.click()}>
            {uploading ? <><Spinner data-icon="inline-start" />上传中...</> : <><Upload data-icon="inline-start" />上传简历</>}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><Spinner className="size-8 text-primary" /></div>
      ) : resumes.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center text-center py-12">
            <FileText className="size-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground">
              {searchQuery ? '未找到匹配的简历' : '暂无简历'}
            </h3>
            <p className="text-sm text-muted-foreground/60 mt-1">
              {searchQuery ? '尝试其他搜索关键词' : '点击上方按钮上传你的第一份简历'}
            </p>
              </CardContent>
            </Card>
          ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>文件名</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>上传时间</TableHead>
              <TableHead>操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {resumes.map((resume) => (
              <TableRow key={resume.id}>
                <TableCell>
                  <div className="flex items-center gap-2 font-medium">
                    <FileText className="size-4 text-muted-foreground" />
                    {resume.title}
                  </div>
                </TableCell>
                <TableCell><StatusBadge status={resume.status} /></TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(resume.created_at).toLocaleString('zh-CN')}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Link to={`/resumes/${resume.id}`}>
                      <Button variant="ghost" size="sm">详情</Button>
                    </Link>
                    <Button
                      variant="ghost" size="sm"
                      onClick={() => window.open(`/api/v1/resumes/${resume.id}/file?token=${localStorage.getItem('access_token')}`, '_blank')}
                    >
                      <Eye className="size-4" />
                    </Button>
                    <Button
                      variant="ghost" size="sm"
                      onClick={() => {
                        const a = document.createElement('a');
                        a.href = `/api/v1/resumes/${resume.id}/file?token=${localStorage.getItem('access_token')}&download=1`;
                        a.download = resume.title;
                        a.click();
                      }}
                    >
                      <Download className="size-4" />
                    </Button>
                    <Button
                      variant="ghost" size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(resume)}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除简历</AlertDialogTitle>
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
