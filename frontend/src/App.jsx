import { useState, useEffect } from "react";
import axios from "axios";
import { GitBranch, Loader2, Send } from "lucide-react";
import { Analytics } from "./components/Analytics";
import { CommitCard } from "./components/CommitCard";
import { CommitDetails } from "./components/CommitDetails";

// Replace with actual API URL
const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [commits, setCommits] = useState([]);
  const [selectedCommit, setSelectedCommit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sendingMsg, setSendingMsg] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE_URL}/api/data`);
      setCommits(res.data.data || []);
      if (res.data.data?.length > 0) {
        setSelectedCommit(res.data.data[0]);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to fetch commit data. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleTestTelegram = async () => {
    try {
      setSendingMsg(true);
      await axios.get(`${API_BASE_URL}/test-telegram`);
      alert("Telegram message sent successfully!");
    } catch (err) {
      alert("Failed to send telegram message.");
    } finally {
      setSendingMsg(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-900 text-white">
        <Loader2 className="w-10 h-10 animate-spin text-accent-blue" />
        <span className="ml-4 text-xl">Loading AI Insights...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-900 text-white">
        <div className="glass-panel p-8 text-center max-w-md">
          <p className="text-accent-rose text-lg mb-4">{error}</p>
          <button onClick={fetchData} className="px-6 py-2 bg-accent-blue text-white rounded-lg hover:bg-blue-600 transition-colors">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-10 font-sans">
      <header className="flex flex-col md:flex-row justify-between items-center mb-10 gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-accent-blue to-accent-purple rounded-2xl shadow-lg shadow-accent-purple/20">
            <GitBranch className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
              Git AI Agent
            </h1>
            <p className="text-sm text-slate-400 font-medium tracking-wide">Autonomous Code Review & Analysis</p>
          </div>
        </div>
        
        <button 
          onClick={handleTestTelegram}
          disabled={sendingMsg}
          className="flex items-center gap-2 px-6 py-2.5 bg-dark-800 border border-white/10 hover:border-accent-blue/50 text-slate-200 rounded-xl transition-all shadow-lg hover:shadow-accent-blue/10 disabled:opacity-50"
        >
          {sendingMsg ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 text-accent-blue" />}
          <span>Send Test Telegram</span>
        </button>
      </header>

      <div className="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <Analytics commits={commits} />
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="w-full lg:w-1/3 flex flex-col gap-4">
          <h2 className="text-xl font-bold text-slate-200 mb-2 flex items-center gap-2">
            <span className="w-2 h-6 bg-accent-blue rounded-full"></span>
            Recent Commits
          </h2>
          <div className="flex flex-col gap-4 overflow-y-auto max-h-[800px] pr-2 custom-scrollbar">
            {commits.map((commit) => (
              <CommitCard 
                key={commit.commit_sha} 
                commit={commit} 
                isSelected={selectedCommit?.commit_sha === commit.commit_sha}
                onClick={setSelectedCommit}
              />
            ))}
          </div>
        </div>
        
        <div className="w-full lg:w-2/3">
          <div className="glass-panel min-h-[600px] p-6 md:p-8">
            {selectedCommit ? (
              <CommitDetails commit={selectedCommit} />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
                <GitBranch className="w-16 h-16 opacity-20" />
                <p className="text-lg">Select a commit to view AI analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
