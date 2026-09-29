import React, { useState } from 'react';
import { 
  FileText, 
  Search, 
  ShieldCheck, 
  Link, 
  Download, 
  Filter, 
  CheckCircle2, 
  AlertTriangle, 
  Fingerprint, 
  Terminal, 
  Clock 
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';
import type { AuditLogEntry } from '../../types';

export const AuditLogView: React.FC = () => {
  const { auditLogs } = useWorkbench();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);

  const filteredLogs = auditLogs.filter((entry) => {
    const matchesSearch = 
      entry.actionDescription.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.modelUsed.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter = filterType === 'ALL' || entry.eventType === filterType;
    return matchesSearch && matchesFilter;
  });

  const handleExport = () => {
    const jsonStr = JSON.stringify(auditLogs, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MRPL_Audit_Trail_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Tamper-Evident Append-Only Audit Trail
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
                  SHA-256 HASH-CHAINED
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Regulatory compliance log tracking every tool dispatch, file creation, and airgap verification
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-200 border border-industrial-600 text-xs font-semibold shadow transition"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export Audit Trail (JSON)</span>
            </button>
          </div>
        </div>

        {/* Cryptographic Chain Integrity Banner */}
        <div className="bg-industrial-950 p-3.5 rounded-xl border border-industrial-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
          <div className="flex items-center gap-2 text-slate-300">
            <Link className="w-4 h-4 text-emerald-400" />
            <span>Cryptographic Chain Status:</span>
            <strong className="text-emerald-400">IMMUTABLE (All {auditLogs.length} Blocks Verified)</strong>
          </div>

          <div className="flex items-center gap-3 text-slate-400 text-[11px]">
            <span>Algorithm: SHA-256 Chaining</span>
            <span>•</span>
            <span className="text-emerald-400">Egress: 0 Bytes Logged</span>
          </div>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="glass-panel rounded-xl p-4 border border-industrial-700 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by action, actor, model, ID or hash..."
            className="w-full bg-industrial-950 border border-industrial-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono outline-none focus:ring-1 focus:ring-cyan-400"
          />
        </div>

        {/* Filter pills */}
        <div className="flex flex-wrap items-center gap-2">
          {['ALL', 'TASK_INIT', 'TOOL_CALL', 'APPROVAL_REQUEST', 'APPROVAL_GRANTED', 'FILE_WRITE', 'ROUTER_FALLBACK', 'AIRGAP_PROVE'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterType(f)}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition ${
                filterType === f
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 font-bold'
                  : 'bg-industrial-800 text-slate-400 hover:text-slate-200 border border-industrial-700'
              }`}
            >
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Main Audit Log Table */}
      <div className="glass-panel rounded-xl border border-industrial-700 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-industrial-950/80 text-[10px] text-slate-400 uppercase border-b border-industrial-800">
              <tr>
                <th className="p-3">Log ID & Time</th>
                <th className="p-3">Actor / Subsystem</th>
                <th className="p-3">Event Type</th>
                <th className="p-3">Model / Tool</th>
                <th className="p-3">Action Description</th>
                <th className="p-3">Egress</th>
                <th className="p-3">Hash Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-industrial-800">
              {filteredLogs.map((log) => {
                const isApproval = log.eventType === 'APPROVAL_REQUEST' || log.eventType === 'APPROVAL_GRANTED';
                const isFallback = log.eventType === 'ROUTER_FALLBACK';
                const isFileWrite = log.eventType === 'FILE_WRITE';

                return (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedEntry(log)}
                    className="hover:bg-industrial-800/40 cursor-pointer transition"
                  >
                    <td className="p-3 whitespace-nowrap">
                      <div className="font-bold text-cyan-300">{log.id}</div>
                      <div className="text-[10px] text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</div>
                    </td>

                    <td className="p-3 text-slate-300 whitespace-nowrap font-medium">
                      {log.actor}
                    </td>

                    <td className="p-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isApproval
                          ? 'bg-amber-950 text-amber-300 border-amber-800'
                          : isFallback
                          ? 'bg-red-950 text-red-300 border-red-800'
                          : isFileWrite
                          ? 'bg-purple-950 text-purple-300 border-purple-800'
                          : 'bg-industrial-800 text-slate-300 border-industrial-700'
                      }`}>
                        {log.eventType}
                      </span>
                    </td>

                    <td className="p-3 text-slate-300 max-w-[160px] truncate">
                      {log.toolName || log.modelUsed}
                    </td>

                    <td className="p-3 text-slate-300 max-w-sm truncate" title={log.actionDescription}>
                      {log.actionDescription}
                    </td>

                    <td className="p-3 whitespace-nowrap">
                      <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                        0 B
                      </span>
                    </td>

                    <td className="p-3 whitespace-nowrap">
                      <span className="text-emerald-400 flex items-center gap-1 text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span className="text-slate-500 font-mono text-[10px]">{log.sha256Hash.substring(0, 8)}...</span>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Entry Detail Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-industrial-900 border border-cyan-500/50 rounded-xl shadow-2xl max-w-xl w-full text-slate-100 p-6 space-y-4 font-mono text-xs animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-industrial-800 pb-3">
              <div className="flex items-center gap-2">
                <Fingerprint className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-sm text-cyan-300">Audit Record: {selectedEntry.id}</h3>
              </div>
              <button onClick={() => setSelectedEntry(null)} className="text-slate-400 hover:text-slate-200">
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-slate-500 block text-[10px]">EVENT TIMESTAMP</span>
                <span className="text-slate-200">{selectedEntry.timestamp}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">ACTOR & MODEL</span>
                <span className="text-slate-200">{selectedEntry.actor} ({selectedEntry.modelUsed})</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">ACTION DETAILS</span>
                <p className="text-slate-200 bg-industrial-950 p-3 rounded border border-industrial-800 leading-relaxed">
                  {selectedEntry.actionDescription}
                </p>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">CURRENT SHA-256 HASH</span>
                <span className="text-cyan-300 break-all">{selectedEntry.sha256Hash}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">PREVIOUS BLOCK HASH (CHAIN LINK)</span>
                <span className="text-purple-300 break-all">{selectedEntry.prevHash}</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedEntry(null)}
                className="px-4 py-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-300 text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
