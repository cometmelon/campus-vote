import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkAuth = useCallback(async () => {
        const token = api.getToken();
        if (token) {
            try {
                const userData = await api.getMe();
                setUser(userData);
            } catch (error) {
                console.error('Auth check failed:', error);
                api.clearToken();
                setUser(null);
            }
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    const login = async (studentId, password) => {
        setLoading(true);
        try {
            await api.login(studentId, password);
            const userData = await api.getMe();
            setUser(userData);
            return userData;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        api.logout();
        setUser(null);
    };

    const isAuthenticated = !!user;
    const isAdmin = user?.role === 'admin';
    const isStudent = user?.role === 'student';

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            login,
            logout,
            isAuthenticated,
            isAdmin,
            isStudent
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
