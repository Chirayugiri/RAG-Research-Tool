import { AppProvider, useAppContext } from './context/AppContext';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatContainer } from './components/ChatContainer';
import { InputBox } from './components/InputBox';
import { AuthModal } from './components/AuthModal';
import './App.css';

function AppContent() {
  const { isAuthenticated } = useAppContext();

  if (!isAuthenticated) {
    return <AuthModal />;
  }

  return (
    <div className="app">
      <Header />
      <div className="app-body">
        <Sidebar />
        <div className="main-content">
          <ChatContainer />
          <InputBox />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;

