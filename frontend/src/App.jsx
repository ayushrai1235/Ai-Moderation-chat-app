import { AuthProvider, useAuth } from './context/AuthContext';
import { AuthPage } from './pages/AuthPage';
import { ChatLayout } from './components/ChatLayout';
import { Loader } from 'lucide-react';

const AppContent = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="h-screen w-screen flex items-center justify-center bg-[#111b21] text-white">
                 <Loader className="animate-spin text-green-500" size={48} />
            </div>
        );
    }

    if (!user) {
        return <AuthPage />;
    }

    return <ChatLayout />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
export default App;
