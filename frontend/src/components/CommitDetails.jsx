import { ShieldAlert, BookOpen, Settings, Zap, ArrowRight, UserCheck } from "lucide-react";

const Section = ({ title, icon: Icon, children, colorClass }) => (
  <div className="glass-panel mb-6">
    <div className="flex items-center gap-3 mb-4 border-b border-white/10 pb-3">
      <div className={`p-2 rounded-lg ${colorClass}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
    </div>
    <div className="text-slate-300 text-sm leading-relaxed space-y-3">
      {children}
    </div>
  </div>
);

export function CommitDetails({ commit }) {
  if (!commit) return null;

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">{commit.commit_message.split("\n")[0]}</h2>
        <div className="flex flex-wrap gap-3">
          <span className="px-3 py-1 bg-dark-700/50 rounded-full text-xs font-mono text-accent-blue border border-accent-blue/20">
            {commit.commit_sha}
          </span>
          <span className="px-3 py-1 bg-dark-700/50 rounded-full text-xs text-slate-400 border border-white/10">
            {commit.repo_name}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="space-y-6">
          {commit.developer_analysis && (
            <Section title="Developer Analysis" icon={BookOpen} colorClass="bg-accent-blue/80">
              <p><strong className="text-white">Feature Type:</strong> {commit.developer_analysis.feature_type}</p>
              <p><strong className="text-white">Complexity:</strong> {commit.developer_analysis.complexity}</p>
              <p>{commit.developer_analysis.implementation_summary}</p>
            </Section>
          )}

          {commit.orchestrator_decision && (
            <Section title="Orchestrator Decision" icon={Settings} colorClass="bg-slate-600">
              <p>{commit.orchestrator_decision.reasoning}</p>
              <div className="flex gap-2 mt-2">
                {commit.orchestrator_decision.run_security_review && <span className="bg-accent-rose/20 text-accent-rose px-2 py-1 rounded text-xs">Security Check</span>}
                {commit.orchestrator_decision.run_architecture_review && <span className="bg-accent-purple/20 text-accent-purple px-2 py-1 rounded text-xs">Architecture Check</span>}
                {commit.orchestrator_decision.run_better_approach_review && <span className="bg-accent-blue/20 text-accent-blue px-2 py-1 rounded text-xs">Better Approach Check</span>}
              </div>
            </Section>
          )}

          {commit.better_approach_review?.has_better_approach && (
            <Section title="Better Approach" icon={Zap} colorClass="bg-yellow-500/80">
              <p>{commit.better_approach_review.reasoning}</p>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-dark-900/80 p-3 rounded-lg border border-red-500/20">
                  <span className="text-xs text-red-400 font-semibold mb-2 block">Current</span>
                  <pre className="text-xs overflow-x-auto text-slate-300 font-mono">
                    {commit.better_approach_review.current_implementation}
                  </pre>
                </div>
                <div className="bg-dark-900/80 p-3 rounded-lg border border-green-500/20">
                  <span className="text-xs text-green-400 font-semibold mb-2 block">Suggested</span>
                  <pre className="text-xs overflow-x-auto text-slate-300 font-mono">
                    {commit.better_approach_review.suggested_implementation}
                  </pre>
                </div>
              </div>
            </Section>
          )}

          {commit.architecture_review && (
            <Section title="Architecture Review" icon={Settings} colorClass={commit.architecture_review.is_solid ? "bg-accent-emerald/80" : "bg-orange-500/80"}>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-white font-medium">Architecture status:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${commit.architecture_review.is_solid ? 'bg-accent-emerald/20 text-accent-emerald' : 'bg-orange-500/20 text-orange-400'}`}>
                  {commit.architecture_review.is_solid ? 'Solid' : 'Needs Improvement'}
                </span>
              </div>
              
              {commit.architecture_review.strengths?.length > 0 && (
                <div className="mt-3">
                  <strong className="text-emerald-400 block mb-1">Strengths:</strong>
                  <ul className="list-disc pl-5 space-y-1">
                    {commit.architecture_review.strengths.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
              {commit.architecture_review.weaknesses?.length > 0 && (
                <div className="mt-3">
                  <strong className="text-orange-400 block mb-1">Weaknesses:</strong>
                  <ul className="list-disc pl-5 space-y-1">
                    {commit.architecture_review.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}
              {commit.architecture_review.recommendations?.length > 0 && (
                <div className="mt-3">
                  <strong className="text-accent-blue block mb-1">Recommendations:</strong>
                  <ul className="list-disc pl-5 space-y-1">
                    {commit.architecture_review.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
            </Section>
          )}
        </div>

        <div className="space-y-6">
          {commit.security_review && (
            <Section title="Security Review" icon={ShieldAlert} colorClass={commit.security_review.is_secure ? "bg-accent-emerald/80" : "bg-accent-rose/80"}>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-white font-medium">Risk Level:</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${commit.security_review.is_secure ? 'bg-accent-emerald/20 text-accent-emerald' : 'bg-accent-rose/20 text-accent-rose'}`}>
                  {commit.security_review.risk_level || 'Low'}
                </span>
              </div>
              
              {commit.detected_vulnerabilities?.length > 0 && (
                <div className="mt-3">
                  <strong className="text-white block mb-2">Vulnerabilities:</strong>
                  <ul className="list-disc pl-5 space-y-1 text-accent-rose/90">
                    {commit.detected_vulnerabilities.map((v, i) => (
                      <li key={i}>{v.description}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Section>
          )}

          {commit.principal_review && (
            <Section title="Principal Review" icon={UserCheck} colorClass="bg-accent-purple/80">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-white font-medium">Verdict:</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    commit.principal_review.approval_status === 'APPROVED' ? 'bg-accent-emerald/20 text-accent-emerald' : 'bg-accent-rose/20 text-accent-rose'
                  }`}>
                    {commit.principal_review.approval_status}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-white font-medium">Score:</span>
                  <span className="text-xl font-bold text-accent-purple">{commit.principal_review.overall_score}/10</span>
                </div>
              </div>
              
              <p className="italic text-slate-400 border-l-2 border-accent-purple/50 pl-3 py-1 my-4">
                "{commit.principal_review.verdict}"
              </p>

              {commit.priority_fixes?.length > 0 && (
                <div className="mt-4">
                  <strong className="text-white block mb-2">Priority Fixes Required:</strong>
                  <ul className="space-y-2">
                    {commit.priority_fixes.map((fix, i) => (
                      <li key={i} className="flex gap-2 items-start bg-dark-800/50 p-2 rounded border border-accent-rose/10">
                        <ArrowRight className="w-4 h-4 text-accent-rose mt-0.5 shrink-0" />
                        <span>{fix.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Section>
          )}
        </div>
      </div>
    </div>
  );
}
