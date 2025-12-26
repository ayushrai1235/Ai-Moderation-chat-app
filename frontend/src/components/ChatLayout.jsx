import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../context/AuthContext'; // Import Auth
import { MessageBubble } from './MessageBubble';
import { AdminView } from './AdminView';
import { UserSearchModal } from './UserSearchModal';
import { Send, Paperclip, Shield, LogOut, Plus, MessageSquare } from 'lucide-react';
import axios from 'axios';

export const ChatLayout = () => {
    const { user, token, logout, loading } = useAuth(); // Get user and token
    const [conversations, setConversations] = useState([]);
    
    if (loading && !user) {
        return <div className="flex items-center justify-center h-screen bg-gray-100">Loading...</div>;
    }
    const [activeRoom, setActiveRoom] = useState(null);
    const [showSearch, setShowSearch] = useState(false);
    const [inputText, setInputText] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [showAdmin, setShowAdmin] = useState(false);
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);

    // Fetch conversations on mount
    const fetchConversations = async () => {
        try {
            const res = await axios.get('/api/conversations', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setConversations(res.data);
            if (res.data.length > 0 && !activeRoom) {
               // Optional: Auto-select first? No, let user choose.
            }
        } catch (e) {
            console.error("Fetch conversations failed", e);
        }
    };

    useEffect(() => {
        if (token) fetchConversations();
    }, [token]);

    const { messages, sendMessage, isConnected } = useWebSocket(activeRoom, token);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleCreateChat = async (targetUserId) => {
        try {
            const res = await axios.post('/api/conversations', 
                { target_user_id: targetUserId },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setShowSearch(false);
            await fetchConversations();
            setActiveRoom(res.data.conversation_id);
        } catch (e) {
            console.error("Create chat failed", e);
            alert("Failed to start conversation");
        }
    };

    const handleSend = () => {
        if (inputText.trim()) {
            sendMessage(inputText, 'text');
            setInputText('');
        }
    };
    
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        try {
            // 1. Get Signature
            const signRes = await axios.post('/api/upload/sign', {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const { signature, timestamp, api_key, cloud_name, folder } = signRes.data;

            // 2. Upload to Cloudinary
            // Use 'auto' resource type so Cloudinary detects image/video/raw
            const formData = new FormData();
            formData.append('file', file);
            formData.append('api_key', api_key);
            formData.append('timestamp', timestamp);
            formData.append('signature', signature);
            formData.append('folder', folder);

            const uploadRes = await axios.post(
                `https://api.cloudinary.com/v1_1/${cloud_name}/auto/upload`,
                formData
            );

            const { secure_url, resource_type, format } = uploadRes.data;
            
            // Map Cloudinary types to app types
            // resource_type: 'image', 'video', 'raw'
            let msgType = 'document';
            if (resource_type === 'image') msgType = 'image';
            if (resource_type === 'video') msgType = 'video';
            
            // Send as message
            // Content is filename, type is media type, file_url is the link
            sendMessage(file.name, msgType, secure_url);

        } catch (error) {
            console.error("Upload failed", error);
            alert("File upload failed");
        } finally {
            setIsUploading(false);
            // Reset input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };
    
    // Helper to get active room name
    const activeConvName = conversations.find(c => c.id === activeRoom)?.name || 'Chat';

    return (
        <div className="flex h-screen bg-gray-100 overflow-hidden">
            {showAdmin && <AdminView onClose={() => setShowAdmin(false)} />}
            {showSearch && <UserSearchModal onClose={() => setShowSearch(false)} onStartChat={handleCreateChat} />}
            
            {/* Sidebar */}
            <div className="w-1/4 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                     <div className="flex items-center space-x-2 overflow-hidden">
                        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white font-bold flex-shrink-0">
                            {user?.username?.[0]?.toUpperCase()}
                        </div>
                        <span className="font-semibold text-gray-700 truncate">{user?.username}</span>
                    </div>
                    <div className="flex space-x-1">
                        <button 
                            onClick={() => setShowSearch(true)}
                            className="p-2 text-gray-600 hover:bg-gray-200 rounded-full hover:text-green-600 transition"
                            title="New Chat"
                        >
                            <Plus size={20} />
                        </button>
                        <button 
                            onClick={() => setShowAdmin(true)}
                            className="p-2 text-gray-600 hover:bg-gray-200 rounded-full hover:text-green-600 transition"
                            title="Admin Insights"
                        >
                            <Shield size={20} />
                        </button>
                        <button 
                            onClick={() => logout()}
                            className="p-2 text-gray-600 hover:bg-gray-200 rounded-full hover:text-red-600 transition"
                            title="Logout"
                        >
                            <LogOut size={20} />
                        </button>
                    </div>
                </div>
                
                <div className="flex-1 overflow-y-auto">
                    {conversations.length === 0 ? (
                        <div className="p-8 text-center text-gray-400">
                            <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
                            <p className="text-sm">No chats yet.</p>
                            <button onClick={() => setShowSearch(true)} className="text-green-500 text-sm hover:underline mt-2">Start a new one</button>
                        </div>
                    ) : (
                        conversations.map(conv => (
                            <div
                                key={conv.id}
                                onClick={() => setActiveRoom(conv.id)}
                                className={`p-4 cursor-pointer hover:bg-gray-50 transition border-b border-gray-100 ${activeRoom === conv.id ? 'bg-gray-100 border-l-4 border-green-500' : ''}`}
                            >
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold">
                                        {conv.name[0]?.toUpperCase()}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-medium text-gray-800 truncate">{conv.name}</h3>
                                        <p className="text-xs text-gray-400 truncate">Click to open chat</p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-[#efeae2]">
                {activeRoom ? (
                    <>
                        {/* Header */}
                        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center shadow-sm z-10">
                            <div className="flex items-center space-x-3">
                                 <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-bold">
                                    {activeConvName[0]?.toUpperCase()}
                                </div>
                                <h2 className="text-lg font-semibold text-gray-800">{activeConvName}</h2>
                            </div>
                            <div className="flex items-center space-x-2">
                                <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                <span className="text-sm text-gray-500">{isConnected ? 'Online' : 'Offline'}</span>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-2 bg-[url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')] bg-repeat bg-opacity-10">
                            {messages.map((msg, idx) => (
                                <MessageBubble 
                                    key={msg.id || idx} 
                                    message={msg} 
                                    isOwn={user && msg.user_id === user.id}                                 />
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
                         <MessageSquare size={64} className="mb-4 opacity-20" />
                         <p className="text-lg">Select a conversation to start chatting</p>
                    </div>
                )}
                
                {/* Input Area (Only show if activeRoom) */}
                {activeRoom && (
                    <div className="p-3 bg-gray-50 border-t border-gray-200 flex items-center space-x-2">

                    {/* File Upload Button */}
                    <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileUpload} 
                        className="hidden" 
                        accept="image/*,video/*,.pdf,.doc,.docx,.txt"
                    />
                    <button 
                        onClick={() => fileInputRef.current?.click()}
                        className="p-2 text-gray-500 hover:bg-gray-200 rounded-full transition disabled:opacity-50"
                        disabled={!isConnected || isUploading}
                    >
                        {isUploading ? <span className="animate-spin">⌛</span> : <Paperclip size={20} />}
                    </button>

                    {/* Text Input */}
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Type a message..."
                        className="flex-1 p-2 rounded-lg border border-gray-300 focus:outline-none focus:border-green-500"
                        disabled={!isConnected}
                    />

                    {/* Send Button */}
                    <button 
                        onClick={handleSend}
                        className="p-2 bg-green-500 text-white rounded-full hover:bg-green-600 transition disabled:opacity-50"
                        disabled={!isConnected || (!inputText.trim() && !isUploading)}
                    >
                        <Send size={20} />
                    </button>
                </div>
                )}
            </div>
        </div>
    );
};
