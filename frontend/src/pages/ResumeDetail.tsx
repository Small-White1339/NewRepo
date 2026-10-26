import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getResume, deleteResume, analyzeResume } from '../api/resumes';
import { getErrorMessage } from '../api/errors';
import StatusBadge from '../components/StatusBadge';
import SourceInfo from '../components/SourceInfo';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
} from '@/components/ui/alert-dialog';
import { ArrowLeft, Trash2, Sparkles } from 'lucide-react';
import type { ResumeResponse } from '../types';

export default function ResumeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [resume, setResume] = useState<ResumeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    getResume(id)
      .then(setResume)
      .catch(() => setError('加载简历详情失败'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner className="size-8 text-primary" />
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-3 py-2 text-sm text-destructive">
          {error || '简历不存在'}
        </div>
        <Link to="/resumes"><Button variant="ghost">返回列表</Button></Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Link to="/resumes">
          <Button variant="ghost" size="sm">
            <ArrowLeft data-icon="inline-start" /> 返回
          </Button>
        </Link>
        <h2 className="text-2xl font-bold text-foreground">{resume.title}</h2>
        <StatusBadge status={resume.status} />
        <div className="ml-auto flex gap-2">
          <Button
            variant="outline" size="sm"
            disabled={analyzing}
            onClick={async () => {
              if (!resume) return;
              setError('');
              setAnalyzing(true);
              try {
                const updated = await analyzeResume(resume.id);
                setResume(updated);
              } catch (err) { setError(getErrorMessage(err, 'AI 分析失败')); }
              finally { setAnalyzing(false); }
            }}
          >
            {analyzing ? <><Spinner data-icon="inline-start" />分析中...</> : <><Sparkles data-icon="inline-start" />AI 分析</>}
          </Button>
          <Button
            variant="outline" size="sm"
            className="text-destructive border-destructive/30 hover:text-destructive"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="size-4" /> 删除
          </Button>
        </div>
      </div>

      {error && <p role="alert" className="text-destructive">{error}</p>}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>基本信息</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm">
            <p><span className="font-medium">文件名：</span>{resume.title}</p>
            <SourceInfo name={resume.source_name} url={resume.source_url} importedAt={resume.imported_at} />
            <p><span className="font-medium">状态：</span>
              <span className={resume.status === 'PARSED' ? 'text-emerald-600 font-medium' : resume.status === 'FAILED' ? 'text-destructive' : 'text-muted-foreground'}>
                {resume.status === 'PARSED' ? '已解析' : resume.status === 'FAILED' ? '解析失败' : '待解析'}
              </span>
            </p>
            {resume.parsed_data && (() => {
              const pd = resume.parsed_data as Record<string, unknown>;
              const eduLabels: Record<string, string> = { high_school: '高中', associate: '大专', bachelor: '本科', master: '硕士', phd: '博士' };
              return <>
                <p><span className="font-medium">姓名：</span>{(pd.name as string) || '未知'}</p>
                {(pd.phone as string) && <p><span className="font-medium">手机：</span>{pd.phone as string}</p>}
                {(pd.email as string) && <p><span className="font-medium">邮箱：</span>{pd.email as string}</p>}
                {(pd.education_level as string) && <p><span className="font-medium">学历：</span>{eduLabels[pd.education_level as string] || pd.education_level as string}</p>}
                {(pd.experience_years as number) !== undefined && pd.experience_years !== null && <p><span className="font-medium">工作年限：</span>{pd.experience_years as number} 年</p>}
                {(pd.age as number) !== undefined && pd.age !== null ? <p><span className="font-medium">年龄：</span>{pd.age as number} 岁</p> : <p><span className="font-medium">年龄：</span>未知</p>}
              </>;
            })()}
          </CardContent>
        </Card>

        {/* AI Analysis */}
        {resume.parsed_data && <AiAnalysisCard data={resume.parsed_data} />}

        {/* Skills */}
        <Card>
          <CardHeader>
            <CardTitle>技能</CardTitle>
          </CardHeader>
          <CardContent>
            {resume.skills.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无技能信息</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {resume.skills.map((s, i) => (
                  <Badge key={i} variant="outline">
                    {s.name}
                    {s.level && <span className="ml-1 text-muted-foreground">({s.level})</span>}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Work Experience */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>工作经历</CardTitle>
          </CardHeader>
          <CardContent>
            {resume.work_experiences.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无工作经历</p>
            ) : (
              <div className="flex flex-col gap-4">
                {resume.work_experiences.map((exp, i) => (
                  <div key={i} className="border-l-2 border-primary pl-4">
                    <h4 className="font-semibold">{exp.title}</h4>
                    <p className="text-sm text-muted-foreground">{exp.company}</p>
                    {(exp.start_date || exp.end_date) && (
                      <p className="text-xs text-muted-foreground/60">
                        {exp.start_date || '—'} ~ {exp.end_date || '至今'}
                      </p>
                    )}
                    {exp.description && (
                      <p className="text-sm mt-1 text-muted-foreground/80">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Education */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>教育经历</CardTitle>
          </CardHeader>
          <CardContent>
            {resume.educations.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无教育经历</p>
            ) : (
              <div className="flex flex-col gap-4">
                {resume.educations.map((edu, i) => (
                  <div key={i} className="border-l-2 border-emerald-500 pl-4">
                    <h4 className="font-semibold">{edu.school}</h4>
                    <p className="text-sm text-muted-foreground">
                      {edu.degree && `${edu.degree} · `}{edu.field || ''}
                    </p>
                    {(edu.start_date || edu.end_date) && (
                      <p className="text-xs text-muted-foreground/60">
                        {edu.start_date || '—'} ~ {edu.end_date || '至今'}
                      </p>
                    )}
                    {edu.description && (
                      <p className="text-sm mt-1 text-muted-foreground/80">{edu.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Projects */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>项目经历</CardTitle>
          </CardHeader>
          <CardContent>
            {resume.projects.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无项目经历</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {resume.projects.map((proj, i) => (
                  <div key={i} className="rounded-lg border p-4">
                    <h4 className="font-semibold">{proj.name}</h4>
                    {proj.role && <p className="text-sm text-muted-foreground">角色：{proj.role}</p>}
                    {proj.description && (
                      <p className="text-sm mt-1 text-muted-foreground/80">{proj.description}</p>
                    )}
                    {proj.tech_stack && proj.tech_stack.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {proj.tech_stack.map((t, j) => (
                          <Badge key={j} variant="secondary" className="text-xs">{t}</Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Certificates */}
        {resume.certificates.length > 0 && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>证书</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                {resume.certificates.map((cert, i) => (
                  <div key={i} className="rounded-lg border p-3">
                    <p className="font-medium text-sm">{cert.name}</p>
                    {cert.issuer && <p className="text-xs text-muted-foreground">{cert.issuer}</p>}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {resume.raw_text && <Card>
        <CardHeader><CardTitle>识别的简历原文</CardTitle></CardHeader>
        <CardContent><pre className="whitespace-pre-wrap break-words font-sans text-sm max-h-96 overflow-y-auto">{resume.raw_text}</pre></CardContent>
      </Card>}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除简历</AlertDialogTitle>
            <AlertDialogDescription>
              确认删除「{resume?.title}」？<br />
              关联的匹配分析报告也将同步删除，此操作不可撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowDeleteDialog(false)}>取消</AlertDialogCancel>
            <Button variant="destructive" onClick={async () => {
              if (!resume) return;
              try { await deleteResume(resume.id); navigate('/resumes'); }
              catch { setError('删除失败'); }
              finally { setShowDeleteDialog(false); }
            }}>确认删除</Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

function AiAnalysisCard({ data }: { data: Record<string, unknown> }) {
  const strengths = data.strengths as string[] | undefined;
  const weaknesses = data.weaknesses as string[] | undefined;
  const achievements = data.key_achievements as string[] | undefined;
  const summary = data.summary as string | undefined;
  const educationLevel = data.education_level as string | undefined;
  const eduLabels: Record<string, string> = { high_school: '高中', associate: '大专', bachelor: '本科', master: '硕士', phd: '博士' };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-primary">
          <Sparkles className="size-4" /> AI 智能分析
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 text-sm">
        {summary && <div><p className="font-medium mb-1">摘要</p><p className="text-muted-foreground">{summary}</p></div>}
        {educationLevel && <p><span className="font-medium">最高学历：</span>{eduLabels[educationLevel] || educationLevel}</p>}
        {strengths && strengths.length > 0 && (
          <div><p className="font-medium mb-1">优势</p><ul className="list-disc list-inside text-muted-foreground">{strengths.map((s, i) => <li key={i}>{s}</li>)}</ul></div>
        )}
        {weaknesses && weaknesses.length > 0 && (
          <div><p className="font-medium mb-1">不足</p><ul className="list-disc list-inside text-muted-foreground">{weaknesses.map((w, i) => <li key={i}>{w}</li>)}</ul></div>
        )}
        {achievements && achievements.length > 0 && (
          <div><p className="font-medium mb-1">主要成就</p><ul className="list-disc list-inside text-muted-foreground">{achievements.map((a, i) => <li key={i}>{a}</li>)}</ul></div>
        )}
      </CardContent>
    </Card>
  );
}
