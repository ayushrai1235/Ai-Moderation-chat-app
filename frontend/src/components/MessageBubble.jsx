import React from 'react';
import { format } from 'date-fns';
import { Check, AlertTriangle, Ban } from 'lucide-react';
import clsx from 'clsx';

export const MessageBubble = ({ message, isOwn }) => {
    if (!message) return null;
    const { content, timestamp, status, moderation, type, file_url } = message;

    const formatTime = (ts) => {
        try {
            if (!ts || isNaN(ts)) return '';
            return format(new Date(ts * 1000), 'HH:mm');
        } catch (e) {
            return '';
        }
    };
    
    // Status: pending, allowed, warning, blocked
    const isBlocked = status === 'blocked';
    const isWarning = status === 'warning';

    return (
        <div className={clsx("flex mb-4", isOwn ? "justify-end" : "justify-start")}>
            <div className={clsx(
                "max-w-[70%] rounded-lg p-3 relative shadow-sm",
                isOwn ? "bg-[#d9fdd3]" : "bg-white",
                isBlocked && "bg-red-100 border border-red-300",
                isWarning && "bg-yellow-50 border border-yellow-300"
            )}>
                {/* Header / Warning Label */}
                {isWarning && (
                    <div className="flex items-center text-xs text-yellow-600 mb-1 font-bold">
                        <AlertTriangle size={12} className="mr-1" />
                        Warning: Potentially unsafe content
                    </div>
                )}
                
                {isBlocked ? (
                    <div className="flex flex-col border border-red-200 rounded p-2 bg-red-50">
                        <div className="flex items-center text-red-600 mb-2 border-b border-red-200 pb-2">
                            <Ban size={16} className="mr-2" />
                            <span className="text-xs font-bold">Blocked by AI Moderation (Only you can see this)</span>
                        </div>
                        
                        {/* Content shown with reduced opacity */}
                        <div className="opacity-60 filter grayscale">
                             {/* Media Content */}
                             {type === 'image' && file_url && (
                                <img src={file_url} alt="Shared content" className="rounded-lg mb-2 max-h-64 object-cover" />
                            )}
                            {type === 'video' && file_url && (
                                <video src={file_url} controls className="rounded-lg mb-2 max-h-64" />
                            )}
                            {type === 'document' && file_url && (
                                <a href={file_url} target="_blank" rel="noopener noreferrer" className="flex items-center p-2 bg-gray-100 rounded mb-2 hover:bg-gray-200 transition">
                                    <span className="text-blue-600 underline">View Document</span>
                                </a>
                            )}
                            <p className="text-sm text-gray-800 whitespace-pre-wrap">{content}</p>
                        </div>

                         {/* Explanation */}
                         {moderation?.explanation && (
                             <div className="mt-2 text-xs text-red-600 font-medium">
                                 Reason: {moderation.explanation}
                             </div>
                         )}
                    </div>
                ) : (
                    <>
                        {/* Media Content */}
                        {type === 'image' && file_url && (
                            <img src={file_url} alt="Shared content" className="rounded-lg mb-2 max-h-64 object-cover" />
                        )}
                        {type === 'video' && file_url && (
                            <video src={file_url} controls className="rounded-lg mb-2 max-h-64" />
                        )}
                        {type === 'document' && file_url && (
                            <a href={file_url} target="_blank" rel="noopener noreferrer" className="flex items-center p-2 bg-gray-100 rounded mb-2 hover:bg-gray-200 transition">
                                <span className="text-blue-600 underline">View Document</span>
                            </a>
                        )}

                        {/* Text Content */}
                        <p className="text-sm text-gray-800 whitespace-pre-wrap">{content}</p>
                    </>
                )}

                {/* Metadata */}
                <div className="flex justify-end items-center mt-1 space-x-1">
                    <span className="text-[10px] text-gray-500">
                        {formatTime(timestamp)}
                    </span>
                    {isOwn && (
                        <span className="text-gray-500">
                            <Check size={12} />
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};
