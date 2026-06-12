import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Activity, DollarSign, Brain } from "lucide-react";

export function Analytics({ commits }) {
  if (!commits || commits.length === 0) return null;

  // Prepare data for the charts
  const costData = commits.map(c => {
    const cost = c.llm_usage_logs?.reduce((acc, log) => acc + (log.total_cost || 0), 0) || 0;
    return {
      name: c.commit_sha.substring(0, 5),
      cost: Number(cost.toFixed(4)),
    };
  }).reverse(); // chronological

  const vulnData = commits.map(c => {
    return {
      name: c.commit_sha.substring(0, 5),
      vulns: c.detected_vulnerabilities?.length || 0,
      fixes: c.priority_fixes?.length || 0
    };
  }).reverse();

  const totalCost = costData.reduce((acc, curr) => acc + curr.cost, 0);
  const totalVulns = vulnData.reduce((acc, curr) => acc + curr.vulns, 0);

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-2">
        <div className="glass-panel flex items-center gap-4">
          <div className="p-3 bg-accent-blue/10 rounded-xl">
            <Activity className="text-accent-blue w-6 h-6" />
          </div>
          <div>
            <p className="text-slate-400 text-sm">Total Commits Analyzed</p>
            <p className="text-2xl font-bold text-white">{commits.length}</p>
          </div>
        </div>
        <div className="glass-panel flex items-center gap-4">
          <div className="p-3 bg-accent-emerald/10 rounded-xl">
            <DollarSign className="text-accent-emerald w-6 h-6" />
          </div>
          <div>
            <p className="text-slate-400 text-sm">Total LLM Cost</p>
            <p className="text-2xl font-bold text-white">${totalCost.toFixed(3)}</p>
          </div>
        </div>
        <div className="glass-panel flex items-center gap-4">
          <div className="p-3 bg-accent-rose/10 rounded-xl">
            <Brain className="text-accent-rose w-6 h-6" />
          </div>
          <div>
            <p className="text-slate-400 text-sm">Total Vulnerabilities</p>
            <p className="text-2xl font-bold text-white">{totalVulns}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel h-[300px]">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 px-2">LLM Costs per Commit</h3>
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={costData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                itemStyle={{ color: '#10b981' }}
              />
              <Line type="monotone" dataKey="cost" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2 }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel h-[300px]">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 px-2">Issues Identified</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={vulnData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}/>
              <Bar dataKey="vulns" name="Vulnerabilities" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="fixes" name="Priority Fixes" fill="#a855f7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
