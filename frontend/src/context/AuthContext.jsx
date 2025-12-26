import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            checkAuth(token);
        } else {
            setLoading(false);
        }
    }, []);

    const checkAuth = async (currentToken) => {
        try {
            const res = await axios.get('/api/auth/me', {
                headers: { Authorization: `Bearer ${currentToken}` }
            });
            setUser(res.data);
            localStorage.setItem('token', currentToken);
        } catch (error) {
            console.error("Auth check failed:", error);
            logout(false); // Don't call API on auth check fail (token invalid)
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        const res = await axios.post('/api/auth/login', { email, password });
        const { session_id } = res.data;
        setToken(session_id);
        await checkAuth(session_id);
    };

    const register = async (email, username, password) => {
        await axios.post('/api/auth/register', { email, username, password });
        await login(email, password);
    };

    const logout = async (callApi = true) => {
        try {
            if (callApi && token) {
                await axios.post('/api/auth/logout', {}, {
                   headers: { Authorization: `Bearer ${token}` }
                });
            }
        } catch (e) {
            console.error("Logout error", e);
        } finally {
            setUser(null);
            setToken(null);
            localStorage.removeItem('token');
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
