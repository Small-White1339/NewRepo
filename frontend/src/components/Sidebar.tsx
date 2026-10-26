import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/useAuth';
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Target,
  Bookmark,
} from 'lucide-react';

const navItems = [
  { to: '/', label: '仪表盘', icon: LayoutDashboard },
  { to: '/resumes', label: '简历管理', icon: FileText },
  { to: '/jobs', label: '岗位管理', icon: Briefcase },
  { to: '/matches', label: '匹配分析', icon: Target },
];

const seekerItems = [
  { to: '/', label: '求职概览', icon: LayoutDashboard },
  { to: '/resumes', label: '我的简历', icon: FileText },
  { to: '/opportunities', label: '岗位探索', icon: Briefcase },
  { to: '/career', label: '我的求职', icon: Bookmark },
];

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { isHR } = useAuth();
  return (
    <aside className="flex h-full flex-col gap-2 border-r bg-sidebar p-3">
      <div className="flex items-center gap-2 px-2 py-3">
        <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
          SH
        </div>
        <span className="text-base font-semibold text-sidebar-foreground">SmartHire</span>
      </div>
      <nav className="flex flex-col gap-1">
        {(isHR ? navItems : seekerItems).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                  : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
              )
            }
          >
            <item.icon className="size-4 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
