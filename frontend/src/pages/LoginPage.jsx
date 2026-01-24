import { useState } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Vote, Loader2, User, Lock } from 'lucide-react';

export default function LoginPage() {
    const [, setLocation] = useLocation();
    const { login } = useAuth();
    const [studentId, setStudentId] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(studentId, password);
            setLocation('/dashboard');
        } catch (err) {
            setError(err.message || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <Card className="w-full max-w-md shadow-lg">
                <CardContent className="p-8">
                    {/* Logo and Title */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-4">
                            <Vote className="w-9 h-9 text-white" />
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-1">University Portal</h1>
                        <p className="text-sm text-gray-600">Sign in to access elections and dashboard</p>
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-2">
                            <Label htmlFor="studentId" className="text-sm font-medium text-gray-700">
                                Username / Student ID
                            </Label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <Input
                                    id="studentId"
                                    type="text"
                                    placeholder="Enter your ID"
                                    value={studentId}
                                    onChange={(e) => setStudentId(e.target.value)}
                                    disabled={loading}
                                    required
                                    className="pl-10"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                                Password
                            </Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                    required
                                    className="pl-10"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg border border-red-200">
                                {error}
                            </div>
                        )}

                        <Button type="submit" className="w-full h-11 text-base font-medium" disabled={loading}>
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </Button>
                    </form>

                    {/* Demo credentials */}
                    <div className="mt-6 pt-6 border-t border-gray-200">
                        <p className="text-xs text-gray-500 text-center mb-2">Demo Credentials</p>
                        <div className="space-y-1 text-xs text-gray-600 text-center">
                            <p>Demo Admin: <span className="font-mono font-medium">admin / admin</span></p>
                            <p>Demo Student: <span className="font-mono font-medium">student / student</span></p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
