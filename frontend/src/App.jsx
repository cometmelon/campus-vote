import { Switch, Route, Redirect, useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import { Loader2 } from 'lucide-react';

// Pages
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import ElectionsPage from '@/pages/ElectionsPage';
import VotingPortalPage from '@/pages/VotingPortalPage';
import ClubsPage from '@/pages/ClubsPage';
import VotePage from '@/pages/VotePage';

function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Redirect to="/login" />;
    }

    return children;
}

function AdminRoute({ children }) {
    const { isAdmin, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!isAdmin) {
        return <Redirect to="/dashboard" />;
    }

    return children;
}

export default function App() {
    const { isAuthenticated, loading } = useAuth();
    const [location] = useLocation();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading CampusVote...</p>
                </div>
            </div>
        );
    }

    // Redirect authenticated users away from login
    if (isAuthenticated && location === '/login') {
        return <Redirect to="/dashboard" />;
    }

    // Redirect root to login or dashboard
    if (location === '/') {
        return <Redirect to={isAuthenticated ? '/dashboard' : '/login'} />;
    }

    return (
        <Switch>
            <Route path="/login" component={LoginPage} />

            <Route path="/vote/:token">
                {params => <VotePage token={params.token} />}
            </Route>

            <Route path="/dashboard">
                <ProtectedRoute>
                    <DashboardPage />
                </ProtectedRoute>
            </Route>

            <Route path="/elections">
                <ProtectedRoute>
                    <AdminRoute>
                        <ElectionsPage />
                    </AdminRoute>
                </ProtectedRoute>
            </Route>

            <Route path="/voting-portal">
                <ProtectedRoute>
                    <VotingPortalPage />
                </ProtectedRoute>
            </Route>

            <Route path="/clubs">
                <ProtectedRoute>
                    <ClubsPage />
                </ProtectedRoute>
            </Route>

            <Route>
                <Redirect to={isAuthenticated ? '/dashboard' : '/login'} />
            </Route>
        </Switch>
    );
}
