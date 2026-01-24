import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import MainLayout from '@/components/MainLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Vote, TrendingUp, Users2, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from 'recharts';

export default function DashboardPage() {
    const { isAdmin } = useAuth();

    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['dashboardStats'],
        queryFn: () => api.getDashboardStats(),
        enabled: isAdmin,
    });

    const { data: turnoutData, isLoading: turnoutLoading } = useQuery({
        queryKey: ['departmentTurnout'],
        queryFn: () => api.getDepartmentTurnout(),
        enabled: isAdmin,
    });

    const { data: recentElections, isLoading: electionsLoading } = useQuery({
        queryKey: ['recentElections'],
        queryFn: () => api.getRecentElections(),
        enabled: isAdmin,
    });

    // Student Dashboard - redirect to voting portal
    if (!isAdmin) {
        return (
            <MainLayout>
                <div className="text-center py-12">
                    <Vote className="w-16 h-16 mx-auto mb-4 text-primary" />
                    <h2 className="text-2xl font-bold mb-2">Welcome, Student!</h2>
                    <p className="text-gray-600">Please visit the Voting Portal to participate in elections.</p>
                </div>
            </MainLayout>
        );
    }

    // Admin Dashboard
    return (
        <MainLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
                    <p className="text-gray-600 mt-1">Real-time insights into campus election activities.</p>
                </div>

                {/* KPI Cards */}
                <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
                    {statsLoading ? (
                        Array(4).fill(0).map((_, i) => (
                            <Card key={i} className="animate-pulse">
                                <CardContent className="p-6 h-28 bg-gray-100" />
                            </Card>
                        ))
                    ) : (
                        <>
                            <Card className="border-0 shadow-sm">
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600 mb-1">Total Students</p>
                                            <p className="text-3xl font-bold text-gray-900">{stats?.total_students || 1}</p>
                                            <p className="text-xs text-green-600 mt-1">+12%</p>
                                        </div>
                                        <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
                                            <Users className="w-6 h-6 text-blue-600" />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card className="border-0 shadow-sm">
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600 mb-1">Active Elections</p>
                                            <p className="text-3xl font-bold text-gray-900">{stats?.active_elections || 0}</p>
                                            <p className="text-xs text-green-600 mt-1">Currently Live</p>
                                        </div>
                                        <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center">
                                            <Vote className="w-6 h-6 text-purple-600" />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card className="border-0 shadow-sm">
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600 mb-1">Voter Turnout</p>
                                            <p className="text-3xl font-bold text-gray-900">{stats?.voter_turnout || 200}%</p>
                                            <p className="text-xs text-green-600 mt-1">+5.2%</p>
                                        </div>
                                        <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center">
                                            <TrendingUp className="w-6 h-6 text-indigo-600" />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card className="border-0 shadow-sm">
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600 mb-1">Registered Clubs</p>
                                            <p className="text-3xl font-bold text-gray-900">{stats?.registered_clubs || 1}</p>
                                        </div>
                                        <div className="w-12 h-12 rounded-xl bg-pink-50 flex items-center justify-center">
                                            <Users2 className="w-6 h-6 text-pink-600" />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    )}
                </div>

                {/* Charts Row */}
                <div className="grid gap-6 lg:grid-cols-2">
                    {/* Department Turnout Chart */}
                    <Card className="border-0 shadow-sm">
                        <CardContent className="p-6">
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Department Turnout</h3>
                                <p className="text-sm text-gray-600">Voter participation by department</p>
                            </div>
                            {turnoutLoading ? (
                                <div className="h-72 flex items-center justify-center">
                                    <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                                </div>
                            ) : turnoutData && turnoutData.length > 0 ? (
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={turnoutData} layout="vertical" margin={{ left: 10, right: 10 }}>
                                            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
                                            <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
                                            <YAxis type="category" dataKey="department" width={40} stroke="#9ca3af" fontSize={12} />
                                            <Tooltip
                                                formatter={(value) => `${value}%`}
                                                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                            />
                                            <Bar dataKey="turnout" fill="#6366F1" radius={[0, 4, 4, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            ) : (
                                <div className="h-72 flex items-center justify-center text-gray-400">
                                    No turnout data available
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Recent Elections */}
                    <Card className="border-0 shadow-sm">
                        <CardContent className="p-6">
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Recent Elections</h3>
                                <p className="text-sm text-gray-600">Latest scheduled or active votes</p>
                            </div>
                            {electionsLoading ? (
                                <div className="space-y-3">
                                    {Array(4).fill(0).map((_, i) => (
                                        <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                                    ))}
                                </div>
                            ) : recentElections && recentElections.length > 0 ? (
                                <div className="space-y-3">
                                    {recentElections.map((election, idx) => (
                                        <div key={election.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                            <div className="flex items-center gap-3">
                                                <div className="w-2 h-2 rounded-full bg-primary"></div>
                                                <div>
                                                    <p className="font-medium text-gray-900 text-sm">{election.title}</p>
                                                    <p className="text-xs text-gray-500">
                                                        {new Date(election.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {new Date(election.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                                    </p>
                                                </div>
                                            </div>
                                            <Badge
                                                variant={election.status === 'active' ? 'default' : election.status === 'planned' ? 'secondary' : 'outline'}
                                                className="capitalize"
                                            >
                                                {election.status}
                                            </Badge>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="h-64 flex items-center justify-center text-gray-400">
                                    No elections yet
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Welcome Message */}
                <Card className="border-0 shadow-sm bg-gradient-to-r from-primary/5 to-purple-50">
                    <CardContent className="p-6">
                        <h3 className="font-semibold text-gray-900 mb-1">Welcome back!</h3>
                        <p className="text-sm text-gray-600">You have successfully logged in.</p>
                    </CardContent>
                </Card>
            </div>
        </MainLayout>
    );
}
