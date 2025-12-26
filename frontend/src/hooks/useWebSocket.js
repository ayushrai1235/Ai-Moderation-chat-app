import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';

export const useWebSocket = (roomId, token) => {
    const [messages, setMessages] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef(null);

    useEffect(() => {
        if (!roomId || !token) return;

        // Reset messages and fetch history
        setMessages([]);
        const fetchHistory = async () => {
             try {
                 const res = await axios.get(`/api/history/${roomId}`);
                 // Normalize timestamp if needed (db uses created_at)
                 const history = res.data.map(msg => ({
                     ...msg,
                     timestamp: msg.timestamp || (msg.created_at ? new Date(msg.created_at).getTime() / 1000 : Date.now() / 1000)
                 }));
                 setMessages(history);
             } catch (e) {
                 console.error("Failed to fetch history", e);
             }
        };
        fetchHistory();

        // Connect to WebSocket with token
        const socket = new WebSocket(`ws://localhost:8000/ws/${roomId}/${token}`);
        
        socket.onopen = () => {
            console.log('Connected to WebSocket');
            setIsConnected(true);
        };

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                // Ensure timestamp exists
                if (!message.timestamp) message.timestamp = Date.now() / 1000;
                
                setMessages((prev) => [...prev, message]);
            } catch (e) {
                console.error('Error parsing message:', e);
            }
        };

        socket.onclose = (e) => {
            console.log('Disconnected from WebSocket', e.code);
            setIsConnected(false);
        };

        ws.current = socket;

        return () => {
            socket.close();
        };
    }, [roomId, token]);

    const sendMessage = useCallback((content, type = 'text', fileUrl = null) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const message = {
                content,
                type, // 'text', 'image', 'document', 'video'
                file_url: fileUrl,
                timestamp: Date.now()
            };
            ws.current.send(JSON.stringify(message));
        }
    }, []);

    return { messages, sendMessage, isConnected };
};
