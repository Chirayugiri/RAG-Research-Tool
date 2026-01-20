import { AppProvider } from './context/AppContext';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatContainer } from './components/ChatContainer';
import { InputBox } from './components/InputBox';
import './App.css';

function App() {
  return (
    <AppProvider>
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
    </AppProvider>
  );
}

export default App;
