import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { ShieldAlert, RefreshCw } from 'lucide-react';

export const AdminView = ({ onClose }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const res = await axios.get('/api/moderation/logs');
            setLogs(res.data);
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <div className="fixed inset-0 bg-white z-50 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <div className="flex items-center space-x-2">
                    <ShieldAlert className="text-red-600" />
                    <h2 className="text-xl font-bold text-gray-800">Moderation Insights</h2>
                </div>
                <div className="flex space-x-2">
                    <button 
                        onClick={fetchLogs} 
                        className="p-2 text-gray-600 hover:bg-gray-200 rounded flex items-center"
                    >
                        <RefreshCw size={18} className={`mr-1 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                    <button 
                        onClick={onClose} 
                        className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700"
                    >
                        Close
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto p-6 bg-gray-100">
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Room</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {logs.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                                        No flagged messages found.
                                    </td>
                                </tr>
                            ) : (
                                logs.map((log, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {log.timestamp ? format(new Date(log.timestamp * 1000), 'MMM d, HH:mm') : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.user_id}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.room_id}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                                            {log.moderation?.category || '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                ${log.moderation?.severity === 'high' ? 'bg-red-100 text-red-800' : 
                                                  log.moderation?.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                                                  'bg-green-100 text-green-800'}`}>
                                                {log.moderation?.severity || 'low'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <span className={log.moderation?.action === 'block' ? 'text-red-600' : 'text-yellow-600'}>
                                                {log.moderation?.action?.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                                            {log.content}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
