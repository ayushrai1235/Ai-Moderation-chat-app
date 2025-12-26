import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Search, UserPlus, X, Loader } from 'lucide-react';

export const UserSearchModal = ({ onClose, onStartChat }) => {
    const { token } = useAuth();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        
        setLoading(true);
        try {
            const res = await axios.get(`/api/users/search?q=${query}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setResults(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                    <h2 className="text-lg font-semibold text-gray-800">New Conversation</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-4">
                    <form onSubmit={handleSearch} className="relative mb-4">
                        <input
                            type="text"
                            placeholder="Search users by name or email..."
                            className="w-full pl-10 pr-4 py-3 bg-gray-100 border-none rounded-lg focus:ring-2 focus:ring-green-500 transition-all outline-none"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            autoFocus
                        />
                        <Search className="absolute left-3 top-3.5 text-gray-400" size={20} />
                        <button type="submit" hidden>Search</button>
                    </form>

                    <div className="space-y-2 max-h-[300px] overflow-y-auto">
                        {loading ? (
                            <div className="flex justify-center py-8">
                                <Loader className="animate-spin text-green-500" />
                            </div>
                        ) : results.length > 0 ? (
                            results.map(user => (
                                <button
                                    key={user.id}
                                    onClick={() => onStartChat(user.id)}
                                    className="w-full flex items-center p-3 hover:bg-gray-50 rounded-lg transition-colors group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-semibold mr-3">
                                        {user.username[0].toUpperCase()}
                                    </div>
                                    <div className="text-left flex-1">
                                        <h3 className="font-medium text-gray-800">{user.username}</h3>
                                        <p className="text-xs text-gray-500">{user.email}</p>
                                    </div>
                                    <UserPlus size={18} className="text-gray-300 group-hover:text-green-500 transition-colors" />
                                </button>
                            ))
                        ) : query && (
                            <p className="text-center text-gray-400 py-8">No users found.</p>
                        )}
                        
                        {!query && !loading && (
                            <p className="text-center text-gray-400 py-8 text-sm">Type to search for people to chat with.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
