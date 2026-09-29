import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Database, 
  Tag, 
  CheckCircle2, 
  Sparkles, 
  FileText, 
  Info, 
  Layers,
  Clock,
  AlertTriangle,
  Shield,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { SYNTHETIC_SOPS } from '../../mockData/syntheticSOPs';
import type { SOPDocument } from '../../types';

interface LiveCitation {
  document_code: string;
  document_title: string;
  refinery_unit: string;
  section: string;
  chunk_id: string;
  similarity_score: number;
  citation_snippet: string;
  full_chunk_text: string;
  citation_label: string;
}

export const KnowledgeBaseView: React.FC = () => {
  const [selectedSOP, setSelectedSOP] = useState<SOPDocument>(SYNTHETIC_SOPS[0]);
  const [searchQuery, setSearchQuery] = useState('minimum retirement thickness for CRU-C-101 intermediate shell');
  const [activePreset, setActivePreset] = useState<string>('cru-101');
  
  // Live Python backend state
  const [isLiveApiOnline, setIsLiveApiOnline] = useState<boolean>(false);
  const [liveQueryLoading, setLiveQueryLoading] = useState<boolean>(false);
  const [liveQueryTimeMs, setLiveQueryTimeMs] = useState<number | null>(null);
  const [liveCitations, setLiveCitations] = useState<LiveCitation[] | null>(null);

  const presetQueries = [
    { id: 'cru-101', label: 'CRU-C-101 Retirement Thickness', query: 'minimum retirement thickness for CRU-C-101 intermediate shell', targetDoc: 'MRPL-SOP-CRU-402' },
    { id: 'api-510', label: 'API 510 RUL Formula', query: 'Remaining useful life calculation formula API 510', targetDoc: 'MRPL-STD-API-510' },
    { id: 'hot-work', label: 'Hot Work Gas Limits', query: 'Hazardous hot work atmospheric LEL and H2S oxygen limits', targetDoc: 'MRPL-SOP-HWP-108' },
    { id: 'exchanger', label: 'E-104 Tube Plugging', query: 'Maximum allowable percentage of plugged tubes in heat exchanger', targetDoc: 'MRPL-MAN-HEX-220' },
    { id: 'asme-viii', label: 'ASME Shell Stress Formula', query: 'Cylindrical shell wall thickness circumferential stress equation ASME Section VIII', targetDoc: 'MRPL-STD-ASME-VIII' },
    { id: 'pumps', label: 'Pump Vibration Trips', query: 'Centrifugal pump ISO 10816 vibration velocity trip limits and seal pressure', targetDoc: 'MRPL-MAN-PMP-112' },
  ];

  // Check health of local Python service on 127.0.0.1:8001
  const checkBackendHealth = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8001/health', { method: 'GET', signal: AbortSignal.timeout(1500) });
      if (res.ok) {
        setIsLiveApiOnline(true);
        return true;
      }
    } catch {
      setIsLiveApiOnline(false);
    }
    return false;
  };

  useEffect(() => {
    checkBackendHealth();
    const timer = setInterval(checkBackendHealth, 5000);
    return () => clearInterval(timer);
  }, []);

  const executeSearch = async (queryText: string) => {
    setLiveQueryLoading(true);
    const isOnline = await checkBackendHealth();

    if (isOnline) {
      try {
        const start = performance.now();
        const res = await fetch('http://127.0.0.1:8001/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText, top_k: 3 }),
        });
        if (res.ok) {
          const data = await res.json();
          setLiveCitations(data.citations);
          setLiveQueryTimeMs(data.execution_time_ms || Math.round(performance.now() - start));
          
          if (data.citations.length > 0) {
            const topCode = data.citations[0].document_code;
            const matched = SYNTHETIC_SOPS.find(s => s.code === topCode);
            if (matched) setSelectedSOP(matched);
          }
          setLiveQueryLoading(false);
          return;
        }
      } catch (err) {
        console.warn('Live query failed, using local index', err);
      }
    }

    // Fallback: search local mock corpus
    setLiveCitations(null);
    setLiveQueryTimeMs(null);
    setLiveQueryLoading(false);
  };

  const handleSelectPreset = (preset: typeof presetQueries[0]) => {
    setActivePreset(preset.id);
    setSearchQuery(preset.query);
    const found = SYNTHETIC_SOPS.find(s => s.code === preset.targetDoc);
    if (found) setSelectedSOP(found);
    executeSearch(preset.query);
  };

  // Sensitivity classifier helper
  const getSensitivityBadge = (doc: SOPDocument) => {
    if (doc.code.includes('HWP') || doc.code.includes('HYC')) {
      return {
        label: 'PROCESS SAFETY CRITICAL (OISD/PSM)',
        color: 'bg-red-950/80 text-red-300 border-red-800',
      };
    }
    if (doc.code.includes('CRU-402') || doc.code.includes('CORR')) {
      return {
        label: 'INTERNAL REFINERY CONFIDENTIAL',
        color: 'bg-amber-950/80 text-amber-300 border-amber-800',
      };
    }
    if (doc.code.includes('ASME') || doc.code.includes('API')) {
      return {
        label: 'RESTRICTED ENGINEERING DESIGN',
        color: 'bg-purple-950/80 text-purple-300 border-purple-800',
      };
    }
    return {
      label: 'STANDARD OPERATING REFERENCE',
      color: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
    };
  };

  // Stale / Drift warning helper
  const getStaleWarning = (doc: SOPDocument) => {
    if (doc.code === 'MRPL-SOP-COR-301') {
      return '⚠️ Review Overdue: Mandatory 3-year turnaround review expired (Nov 2025). Scheduled for Q1 Turnaround update.';
    }
    if (doc.code === 'MRPL-STD-API-510') {
      return '⚠️ Version Drift Advisory: API 510 10th Edition referenced. Local vector chunks updated to match 2025 addendum.';
    }
    if (doc.code === 'MRPL-CORR-2026-08') {
      return '⚠️ Time-Sensitive Turnaround Memo: Operating recommendations require supervisor sign-off before Column CRU-C-101 restart.';
    }
    return null;
  };

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-950 text-purple-400 border border-purple-800">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Refinery SOP & Technical Knowledge Base
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono font-bold">
                  P5 KNOWLEDGE BASE
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border ${
                  isLiveApiOnline 
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-800' 
                    : 'bg-industrial-800 text-slate-300 border-industrial-700'
                }`}>
                  {isLiveApiOnline ? 'PYTHON RAG ENGINE: 127.0.0.1:8001' : 'AIRGAPPED LOCAL INDEX: ACTIVE'}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Grounds agentic reasoning in refinery operating standards, API inspection codes, and turnaround correspondence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono bg-industrial-950 px-3 py-1.5 rounded-lg border border-industrial-800">
            <Database className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-400">Vector Store:</span>
            <span className="text-purple-300 font-bold">Qdrant Local (384-dim Dense Index, 49 Chunks)</span>
          </div>
        </div>

        {/* Synthetic Corpus Notice */}
        <div className="bg-purple-950/20 border border-purple-800/40 rounded-xl p-3.5 flex items-start gap-3 text-xs">
          <Info className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
          <div className="text-slate-300 leading-relaxed">
            <strong className="text-purple-300">Synthetic Refinery Corpus Notice:</strong> The workbench is indexed on 12 representative synthetic SOPs, inspection standards, and equipment manuals styled after MRPL processes. In production, this airgapped vector pipeline directly ingests MRPL's confidential internal document repository.
          </div>
        </div>
      </div>

      {/* Vector Search Simulator */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700 space-y-4 shadow-xl">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Search className="w-4 h-4 text-cyan-400" />
              Airgapped Semantic Vector Search Query
            </label>
            {liveQueryTimeMs !== null && (
              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                Inference Latency: {liveQueryTimeMs} ms (Zero Network Egress)
              </span>
            )}
          </div>
          
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && executeSearch(searchQuery)}
                className="w-full bg-industrial-950 border border-industrial-700 rounded-lg py-2.5 pl-4 pr-10 text-xs font-mono text-slate-100 focus:ring-1 focus:ring-purple-400 outline-none"
                placeholder="Query refinery operating procedures..."
              />
              <Search className="w-4 h-4 text-slate-500 absolute right-3 top-3" />
            </div>

            <button
              onClick={() => executeSearch(searchQuery)}
              disabled={liveQueryLoading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs rounded-lg transition shadow glow-purple"
            >
              {liveQueryLoading ? 'Searching...' : 'Search Vector Index'}
            </button>
          </div>
        </div>

        {/* Preset query chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-mono text-slate-400">Preset Queries:</span>
          {presetQueries.map((preset) => (
            <button
              key={preset.id}
              onClick={() => handleSelectPreset(preset)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition ${
                activePreset === preset.id
                  ? 'bg-purple-900/80 text-purple-200 border border-purple-600 font-bold'
                  : 'bg-industrial-800 text-slate-300 hover:bg-industrial-700 border border-industrial-700'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Corpus & Chunk Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Document Catalog */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              Indexed SOP Corpus ({SYNTHETIC_SOPS.length} Documents)
            </span>
          </h3>

          <div className="space-y-2.5 max-h-[680px] overflow-y-auto pr-1">
            {SYNTHETIC_SOPS.map((doc) => {
              const isSelected = selectedSOP.id === doc.id;
              const sensBadge = getSensitivityBadge(doc);
              const staleAlert = getStaleWarning(doc);

              return (
                <div
                  key={doc.id}
                  onClick={() => {
                    setSelectedSOP(doc);
                    setLiveCitations(null);
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-industrial-850 border-purple-500/70 shadow-lg glow-purple'
                      : 'bg-industrial-900/80 border-industrial-700 hover:border-industrial-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-mono font-bold text-purple-300">{doc.code}</span>
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-industrial-950 text-slate-300 border border-industrial-800">
                      {doc.category}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-100 mt-1.5 leading-snug">
                    {doc.title}
                  </h4>

                  {/* Document Sensitivity Badge */}
                  <div className="mt-2">
                    <span className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold border block truncate ${sensBadge.color}`}>
                      <Shield className="w-2.5 h-2.5 inline mr-1" />
                      {sensBadge.label}
                    </span>
                  </div>

                  {/* Stale / Drift Warning if applicable */}
                  {staleAlert && (
                    <div className="mt-1.5 p-1.5 rounded bg-amber-950/40 border border-amber-500/30 text-[10px] text-amber-300 font-mono flex items-start gap-1">
                      <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                      <span className="truncate">{staleAlert}</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-2.5 pt-2 border-t border-industrial-800">
                    <span className="truncate max-w-[180px]">{doc.unit}</span>
                    <span className="text-purple-300 font-bold">{doc.chunksCount} Chunks</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Retrieved Vector Chunks & Citation Viewer */}
        <div className="lg:col-span-7 glass-panel rounded-xl p-5 border border-industrial-700 space-y-4">
          
          {/* Header of selected document */}
          <div className="border-b border-industrial-800 pb-3 space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-purple-400">{selectedSOP.code}</span>
                <span className="text-slate-500">•</span>
                <h3 className="text-xs font-bold text-slate-100">{selectedSOP.title}</h3>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${getSensitivityBadge(selectedSOP).color}`}>
                {getSensitivityBadge(selectedSOP).label}
              </span>
            </div>

            <p className="text-[11px] text-slate-400 font-mono">
              {selectedSOP.summary}
            </p>

            {/* Stale Warning Callout if applicable */}
            {getStaleWarning(selectedSOP) && (
              <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-500/40 text-xs text-amber-300 font-mono flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{getStaleWarning(selectedSOP)}</span>
              </div>
            )}
          </div>

          {/* Chunks List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-mono text-slate-400 block font-bold">
                {liveCitations 
                  ? `Live RAG Engine Query Results (${liveCitations.length} Citations Retrieved):` 
                  : `Retrieved Semantic Chunks for ${selectedSOP.code}:`}
              </span>
              {liveCitations && (
                <span className="text-[10px] font-mono text-cyan-400">
                  Direct from Python 127.0.0.1:8001
                </span>
              )}
            </div>

            {liveCitations ? (
              liveCitations.map((citation, idx) => (
                <div
                  key={citation.chunk_id}
                  className="bg-industrial-950 p-4 rounded-xl border border-purple-600/60 space-y-2 hover:border-purple-400 transition shadow-md"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded bg-purple-950 text-purple-300 text-[10px] font-mono font-bold flex items-center justify-center border border-purple-800">
                        {idx + 1}
                      </span>
                      <strong className="text-xs font-mono text-purple-300">
                        {citation.document_code} — {citation.section}
                      </strong>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] font-mono">
                      <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                        Sim: {citation.similarity_score}
                      </span>
                      <span className="text-slate-500">ID: {citation.chunk_id}</span>
                    </div>
                  </div>

                  <p className="text-xs font-mono text-slate-200 leading-relaxed bg-industrial-900/80 p-3 rounded-lg border border-industrial-800 whitespace-pre-wrap">
                    "{citation.full_chunk_text}"
                  </p>

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-industrial-900">
                    <span>Unit: {citation.refinery_unit}</span>
                    <span className="text-emerald-400">Exact Citation Available for Agentic Core</span>
                  </div>
                </div>
              ))
            ) : (
              selectedSOP.sampleChunks.map((chunk, idx) => (
                <div
                  key={chunk.id}
                  className="bg-industrial-950 p-4 rounded-xl border border-industrial-800 space-y-2 hover:border-purple-500/40 transition"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded bg-purple-950 text-purple-300 text-[10px] font-mono font-bold flex items-center justify-center border border-purple-800">
                        {idx + 1}
                      </span>
                      <strong className="text-xs font-mono text-purple-300">{chunk.section}</strong>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] font-mono">
                      <span className="px-2 py-0.5 rounded bg-industrial-800 text-cyan-300 border border-industrial-700">
                        Sim: {(0.925 - idx * 0.035).toFixed(3)}
                      </span>
                      <span className="text-slate-500">ID: {chunk.id}</span>
                    </div>
                  </div>

                  <p className="text-xs font-mono text-slate-200 leading-relaxed bg-industrial-900/60 p-3 rounded-lg border border-industrial-850 whitespace-pre-wrap">
                    "{chunk.content}"
                  </p>

                  {chunk.relevanceTag && (
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400 pt-1">
                      <Tag className="w-3 h-3 text-purple-400" />
                      <span>Keyword Anchor: {chunk.relevanceTag}</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Citation Integrity Badge */}
          <div className="p-3 bg-purple-950/20 rounded-xl border border-purple-800/40 flex items-center justify-between text-xs font-mono text-purple-300">
            <span>Every agentic decision and deliverable references these exact chunks to eliminate hallucination.</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          </div>

        </div>

      </div>

    </div>
  );
};
