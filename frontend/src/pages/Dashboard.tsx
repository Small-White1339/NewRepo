import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { listResumes } from '../api/resumes';
import { listJobs } from '../api/jobs';
import { listMatches } from '../api/matches';
import { browseCareerJobs, listCareerReports, listSavedJobs } from '../api/career';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { FileText, Briefcase, Target } from 'lucide-react';

export default function Dashboard() {
  const { user, isHR } = useAuth();
  const [stats, setStats] = useState({ resumes: 0, jobs: 0, matches: 0, saved: 0 });
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setError('');
    Promise.all([
      listResumes().then((r) => r.length),
      (isHR ? listJobs() : browseCareerJobs()).then((j) => j.length),
      (isHR ? listMatches() : listCareerReports()).then((m) => m.filter((item) => item.status === 'COMPLETED').length),
      isHR ? Promise.resolve(0) : listSavedJobs().then((s) => s.length),
    ]).then(([resumes, jobs, matches, saved]) => {
      if (active) setStats({ resumes, jobs, matches, saved });
    }).catch(() => { if (active) setError('概览数据加载失败，请刷新重试。'); });
    return () => { active = false; };
  }, [isHR]);

  const statCards = [
    { to: '/resumes', label: isHR ? '简历总数' : '我的简历', value: stats.resumes, desc: '已上传的简历', icon: FileText, color: 'text-primary' },
    { to: isHR ? '/jobs' : '/opportunities', label: isHR ? '岗位总数' : '可探索岗位', value: stats.jobs, desc: isHR ? '已创建的岗位' : '公开的在招岗位', icon: Briefcase, color: 'text-primary' },
    { to: isHR ? '/matches' : '/career?tab=reports', label: '匹配分析', value: stats.matches, desc: '完成的匹配报告', icon: Target, color: 'text-primary' },
    ...(!isHR ? [{ to: '/career', label: '关注岗位', value: stats.saved, desc: '已收藏的目标岗位', icon: Briefcase, color: 'text-primary' }] : []),
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground">
          欢迎回来，{user?.username}
        </h2>
        <p className="text-muted-foreground mt-1">
          {isHR ? '这是你的 SmartHire 智能招聘辅助系统仪表盘' : '上传简历 → 探索岗位 → 查看匹配度 → 准备投递与面试'}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const content = (
            <Card className="transition-colors hover:bg-muted/50 cursor-pointer">
              <CardContent className="flex flex-col gap-1 pt-6 pb-4">
                <div className="flex items-start justify-between">
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                  <stat.icon className={cn('size-5', stat.color)} />
                </div>
                <span className={cn('text-3xl font-bold', stat.color)}>{stat.value}</span>
                <span className="text-xs text-muted-foreground">{stat.desc}</span>
              </CardContent>
            </Card>
          );

          if (stat.to) {
            return <Link key={stat.label} to={stat.to}>{content}</Link>;
          }
          return <div key={stat.label}>{content}</div>;
        })}
      </div>

      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

      <Card>
        <CardContent className="flex flex-col gap-3 pt-6 pb-4">
          <h3 className="text-base font-medium">快速开始</h3>
          <div className="flex flex-wrap gap-3">
            <Link to="/resumes">
              <Button variant="default" size="sm">上传简历</Button>
            </Link>
            {isHR && <><Link to="/jobs">
              <Button variant="secondary" size="sm">创建岗位</Button>
            </Link>
            <Link to="/matches">
              <Button variant="outline" size="sm">匹配分析</Button>
            </Link></>}
            {!isHR && <><Link to="/opportunities"><Button variant="secondary" size="sm">探索岗位与匹配度</Button></Link><Link to="/career"><Button variant="outline" size="sm">管理我的求职进度</Button></Link></>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
