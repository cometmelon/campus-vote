import { Link, useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import {
    LayoutDashboard,
    Vote,
    Users,
    Mail,
    LogOut,
    Vote as VoteIcon
} from 'lucide-react';

export default function MainLayout({ children }) {
    const { user, logout, isAdmin } = useAuth();
    const [location] = useLocation();

    const adminNavItems = [
        { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/elections', label: 'Elections', icon: Vote },
        { path: '/clubs', label: 'Clubs & Members', icon: Users },
        { path: '/voting-portal', label: 'Voting Portal', icon: Mail },
    ];

    const studentNavItems = [
        { path: '/clubs', label: 'Clubs & Members', icon: Users },
        { path: '/voting-portal', label: 'Voting Portal', icon: VoteIcon },
    ];

    const navItems = isAdmin ? adminNavItems : studentNavItems;

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="w-64 bg-sidebar flex flex-col">
                {/* Logo */}
                <div className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                            <VoteIcon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <span className="text-lg font-bold text-white block leading-tight">CampusVote</span>
                            <span className="text-xs text-sidebar-foreground/60">Admin Console</span>
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav className="flex-1 px-3 space-y-1">
                    {navItems.map(item => {
                        const Icon = item.icon;
                        const isActive = location === item.path;
                        return (
                            <Link key={item.path} href={item.path}>
                                <div className={`
                                    flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all
                                    ${isActive
                                        ? 'bg-primary text-white shadow-lg shadow-primary/20'
                                        : 'text-sidebar-foreground/70 hover:bg-white/5 hover:text-sidebar-foreground'
                                    }
                                `}>
                                    <Icon className="w-5 h-5" />
                                    <span className="text-sm font-medium">{item.label}</span>
                                </div>
                            </Link>
                        );
                    })}
                </nav>

                {/* User section */}
                <div className="p-4 border-t border-white/10">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm">
                            {user?.name?.substring(0, 2).toUpperCase() || 'AD'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                            <p className="text-xs text-sidebar-foreground/60 truncate capitalize">{user?.role}</p>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="text-sidebar-foreground/70 hover:text-white hover:bg-white/5 h-8 w-8"
                            onClick={logout}
                            title="Sign Out"
                        >
                            <LogOut className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
