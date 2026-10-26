import { useEffect, useState, useRef, type ChangeEvent } from 'react';
import { Link } from 'react-router-dom';
import { listResumes, uploadResume, deleteResume } from '../api/resumes';
import { importPublicData } from '../api/imports';
import { getErrorMessage } from '../api/errors';
import SourceInfo from '../components/SourceInfo';
import { useAuth } from '../hooks/useAuth';
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
import { FileText, Upload, Trash2, Search, Eye, Download, ImagePlus, Globe } from 'lucide-react';
import type { ResumeListItem } from '../types';

export default function Resumes() {
  const { isHR } = useAuth();
  const [importing, setImporting] = useState(false);
  const [notice, setNotice] = useState('');
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<ResumeListItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

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
      const result = await uploadResume(file);
      setNotice(result.message);
      e.target.value = '';
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
      <div className="flex flex-wrap gap-3 items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">{isHR ? '简历管理' : '我的简历'}</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            placeholder="搜索姓名、技能或经历..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48"
          />
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md,.markdown,.jpg,.jpeg,.png,.webp,.bmp"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button disabled={uploading} onClick={() => fileInputRef.current?.click()}>
            {uploading ? <><Spinner data-icon="inline-start" />上传中...</> : <><Upload data-icon="inline-start" />上传简历</>}
          </Button>
          <input ref={imageInputRef} type="file" accept=".jpg,.jpeg,.png,.webp,.bmp" className="hidden" onChange={handleFileChange} />
          <Button variant="outline" disabled={uploading} onClick={() => imageInputRef.current?.click()}>
            <ImagePlus data-icon="inline-start" />上传简历照片
          </Button>
          {isHR && <Button variant="outline" disabled={importing} onClick={async () => {
            setImporting(true); setError(''); setNotice('');
            try {
              const result = await importPublicData('resumes');
              setNotice(`新增 ${result.created} 份公开简历，跳过 ${result.skipped} 份重复资料。${result.errors.join(' ')}`);
              await fetchResumes();
            } catch (err) { setError(getErrorMessage(err, '公开简历导入失败')); }
            finally { setImporting(false); }
          }}><Globe data-icon="inline-start" />{importing ? '正在获取公开简历...' : '导入公开简历'}</Button>}
        </div>
      </div>

      <p className="text-sm text-muted-foreground">共 {resumes.length} 份简历。支持 PDF、Word、文本及 JPG / PNG / WEBP / BMP 照片。照片自动识别中英文文字，再提取简历信息。</p>
      {isHR ? <p className="text-xs text-muted-foreground">公开简历保留本人发布的职业经历及来源，已移除联系方式，仅作筛选参考，不代表本人正在求职或向本平台投递。</p>
        : <p className="text-sm text-muted-foreground">你的简历仅供自己管理与分析。上传后可前往 <Link to="/opportunities" className="text-primary underline">岗位探索</Link>，查看匹配度与改进建议。</p>}
      {notice && <p role="status" className="text-sm text-primary">{notice}</p>}

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
                  <SourceInfo name={resume.source_name} url={resume.source_url} importedAt={resume.imported_at} />
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
