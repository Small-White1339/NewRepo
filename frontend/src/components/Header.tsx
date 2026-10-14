import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Menu, LogOut } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-4">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onToggleSidebar}
      >
        <Menu className="size-5" />
      </Button>
      <div className="flex-1">
        <h1 className="text-base font-semibold text-foreground">
          SmartHire 智能招聘辅助系统
        </h1>
      </div>
      <div className="flex items-center gap-2">
        <Avatar className="size-7">
          <AvatarFallback className="text-xs bg-primary text-primary-foreground">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </AvatarFallback>
        </Avatar>
        <span className="hidden sm:inline text-sm font-medium">
          {user?.username}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => { logout(); navigate('/login'); }}
        >
          <LogOut className="size-4" />
          退出登录
        </Button>
      </div>
    </header>
  );
}
