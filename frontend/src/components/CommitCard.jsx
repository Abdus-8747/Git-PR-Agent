import { Shield, Server, FileCode, CheckCircle, AlertTriangle, Bug } from "lucide-react";

export function CommitCard({ commit, onClick, isSelected }) {
  const shortSha = commit.commit_sha.substring(0, 7);
  const title = commit.commit_message.split("\n")[0];
  
  const vulnTotal = commit.detected_vulnerabilities?.length || 0;
  const fixesTotal = commit.priority_fixes?.length || 0;

  return (
    <div 
      onClick={() => onClick(commit)}
      className={`glass-card p-5 cursor-pointer flex flex-col gap-3 group ${isSelected ? 'ring-2 ring-accent-purple bg-dark-800/80' : ''}`}
    >
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-2">
          <FileCode className="w-5 h-5 text-accent-blue" />
          <h3 className="text-lg font-semibold text-white group-hover:text-accent-blue transition-colors truncate max-w-[200px]" title={title}>
            {title || "No Message"}
          </h3>
        </div>
        <span className="text-xs font-mono bg-dark-700/50 px-2 py-1 rounded-md text-slate-300">
          {shortSha}
        </span>
      </div>
      
      <p className="text-sm text-slate-400 truncate">
        {commit.repo_name}
      </p>

      <div className="flex gap-4 mt-2">
        {vulnTotal > 0 && (
          <div className="flex items-center gap-1.5 text-xs text-accent-rose font-medium bg-accent-rose/10 px-2 py-1 rounded-full">
            <Shield className="w-3.5 h-3.5" />
            {vulnTotal} Vulns
          </div>
        )}
        {fixesTotal > 0 && (
          <div className="flex items-center gap-1.5 text-xs text-accent-purple font-medium bg-accent-purple/10 px-2 py-1 rounded-full">
            <Bug className="w-3.5 h-3.5" />
            {fixesTotal} Fixes
          </div>
        )}
        {(vulnTotal === 0 && fixesTotal === 0) && (
          <div className="flex items-center gap-1.5 text-xs text-accent-emerald font-medium bg-accent-emerald/10 px-2 py-1 rounded-full">
            <CheckCircle className="w-3.5 h-3.5" />
            All Clean
          </div>
        )}
      </div>
    </div>
  );
}
