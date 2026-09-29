import React, { useState } from 'react';
import { 
  FileCheck, 
  Download, 
  Check, 
  FileText, 
  Building2, 
  Calendar, 
  UserCheck, 
  Award 
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';

export const DeliverableModal: React.FC = () => {
  const { deliverableModalOpen, setDeliverableModalOpen, activeScenario } = useWorkbench();
  const [downloaded, setDownloaded] = useState(false);

  if (!deliverableModalOpen || !activeScenario.deliverable) return null;

  const doc = activeScenario.deliverable;

  const handleDownload = () => {
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 3000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-industrial-900 border border-cyan-500/40 rounded-xl shadow-2xl max-w-3xl w-full text-slate-100 overflow-hidden glow-cyan animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="bg-industrial-950 border-b border-industrial-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <FileCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-cyan-300 tracking-wide">
                  AIRGAPPED GENERATED DELIVERABLE
                </h3>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-industrial-800 text-slate-300 border border-industrial-700">
                  {doc.type.toUpperCase()} • {doc.size}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                File: {doc.name}
              </p>
            </div>
          </div>

          <button
            onClick={() => setDeliverableModalOpen(false)}
            className="text-slate-400 hover:text-slate-200 text-lg p-1"
          >
            ✕
          </button>
        </div>

        {/* Paper Document Preview (styled like refinery official document) */}
        <div className="p-6 max-h-[70vh] overflow-y-auto space-y-6 text-xs font-sans">
          
          <div className="bg-slate-50 text-slate-900 rounded-lg p-8 shadow-inner border border-slate-300 space-y-6">
            
            {/* Letterhead */}
            <div className="border-b-2 border-red-800 pb-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 text-red-900 font-extrabold text-base tracking-tight">
                  <Building2 className="w-5 h-5 text-red-800" />
                  <span>MANGALORE REFINERY AND PETROCHEMICALS LIMITED</span>
                </div>
                <div className="text-[10px] uppercase tracking-wider text-slate-600 font-semibold">
                  (A Subsidiary of ONGC) • Refinery Operations & Technical Inspection Division
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                  Kuthethoor, Via Katipalla, Mangalore - 575030, Karnataka, India
                </div>
              </div>
              <div className="text-right">
                <span className="inline-block px-2.5 py-1 rounded bg-slate-200 text-slate-800 font-mono font-bold text-[10px] border border-slate-300">
                  OFFICIAL COMPLIANCE NOTE
                </span>
                <div className="text-[10px] text-slate-500 mt-1 font-mono">Ref: MRPL/INSP/CDU2/2026/089</div>
              </div>
            </div>

            {/* Document Title */}
            <div className="text-center py-2">
              <h2 className="text-sm font-bold uppercase tracking-wide text-slate-900">
                {doc.title}
              </h2>
              <div className="text-[11px] text-slate-600 font-mono mt-0.5">
                Governing Standard: <strong className="text-slate-800">{doc.metadata.standard}</strong>
              </div>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-100 p-3 rounded border border-slate-300 text-[11px]">
              <div>
                <span className="text-slate-500 block text-[9px] uppercase font-bold">Refinery Unit</span>
                <strong className="text-slate-800">{doc.metadata.refineryUnit}</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[9px] uppercase font-bold">Execution Engine</span>
                <span className="text-slate-700">{doc.metadata.preparedBy}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[9px] uppercase font-bold">Date of Generation</span>
                <span className="text-slate-700 font-mono">{doc.metadata.date}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[9px] uppercase font-bold">Sign-off Status</span>
                <span className="text-emerald-700 font-semibold">{doc.metadata.approvedBy}</span>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="space-y-1.5">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-1">
                1. Executive Summary & Findings
              </h4>
              <p className="text-slate-700 leading-relaxed text-[11px]">
                {doc.executiveSummary}
              </p>
            </div>

            {/* Structured Table */}
            {doc.tableData && (
              <div className="space-y-2">
                <h4 className="font-bold text-xs uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-1">
                  2. Parameter Verification Matrix
                </h4>
                <div className="overflow-x-auto border border-slate-300 rounded">
                  <table className="w-full text-left text-[11px] font-mono">
                    <thead className="bg-slate-200 text-slate-700 text-[10px] uppercase font-bold">
                      <tr>
                        <th className="p-2 border-b border-slate-300">Parameter</th>
                        <th className="p-2 border-b border-slate-300">Measured Value</th>
                        <th className="p-2 border-b border-slate-300">Threshold / Ref</th>
                        <th className="p-2 border-b border-slate-300">Compliance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {doc.tableData.map((row, idx) => (
                        <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                          <td className="p-2 font-medium text-slate-800">{row.Parameter}</td>
                          <td className="p-2 font-bold text-slate-900">{row.Value}</td>
                          <td className="p-2 text-slate-600">{row.Threshold}</td>
                          <td className="p-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              row.Status === 'NOMINAL' || row.Status === 'ACCEPTABLE'
                                ? 'bg-emerald-100 text-emerald-800'
                                : row.Status === 'ATTENTION' || row.Status === 'ELEVATED'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {row.Status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Signature Block */}
            <div className="pt-6 border-t border-slate-300 grid grid-cols-2 gap-8 text-[10px]">
              <div className="border border-slate-300 p-3 rounded bg-slate-100">
                <span className="text-slate-500 uppercase font-bold block">Autonomous Agent Validation</span>
                <div className="font-mono text-slate-700 mt-1">
                  SHA-256: {doc.sha256.substring(0, 24)}...
                </div>
                <div className="text-emerald-700 font-bold mt-2 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> AIRGAP COMPLIANT (0 BYTES LEAKED)
                </div>
              </div>

              <div className="border border-slate-300 p-3 rounded bg-slate-100 flex flex-col justify-between">
                <div>
                  <span className="text-slate-500 uppercase font-bold block">Refinery Competent Person Sign-Off</span>
                  <div className="text-slate-800 font-semibold mt-1">Chief Plant Inspector (MRPL CDU-II)</div>
                </div>
                <div className="text-slate-500 font-mono mt-2">
                  Digital Timestamp: {new Date().toLocaleDateString()} (Authenticated)
                </div>
              </div>
            </div>

          </div>

        </div>

        {/* Footer */}
        <div className="bg-industrial-950 px-6 py-4 border-t border-industrial-800 flex items-center justify-between">
          <div className="text-slate-400 font-mono text-[11px]">
            Generated via python-docx / openpyxl on airgapped environment
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setDeliverableModalOpen(false)}
              className="px-4 py-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-300 text-xs font-medium"
            >
              Close Preview
            </button>

            <button
              onClick={handleDownload}
              className={`flex items-center gap-1.5 px-5 py-2 rounded-lg text-xs font-semibold shadow transition ${
                downloaded
                  ? 'bg-emerald-600 text-white'
                  : 'bg-cyan-600 hover:bg-cyan-500 text-white glow-cyan'
              }`}
            >
              {downloaded ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Deliverable Exported!</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Deliverable ({doc.type.toUpperCase()})</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
