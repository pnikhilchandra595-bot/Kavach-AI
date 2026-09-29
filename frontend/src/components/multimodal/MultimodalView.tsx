import React, { useState } from 'react';
import { 
  Eye, 
  FileText, 
  Layers, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Scan, 
  ZoomIn, 
  Tag 
} from 'lucide-react';
import { OCR_SAMPLES } from '../../mockData/ocrSamples';
import type { OCRSampleDocument } from '../../mockData/ocrSamples';
import type { OCRFieldExtraction } from '../../types';

export const MultimodalView: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<OCRSampleDocument>(OCR_SAMPLES[0]);
  const [activeExtractionId, setActiveExtractionId] = useState<string | null>(null);

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <Eye className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Multimodal OCR & Engineering Drawing Inspector
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
                  LOCAL VLM + PADDLEOCR
                </span>
              </div>
              <p className="text-xs text-slate-400">
                On-device document ingestion with confidence-flagged extractions and prompt-injection demarcation
              </p>
            </div>
          </div>

          {/* Document Selector Pills */}
          <div className="flex flex-wrap items-center gap-2">
            {OCR_SAMPLES.map((doc) => (
              <button
                key={doc.id}
                onClick={() => {
                  setSelectedDoc(doc);
                  setActiveExtractionId(null);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition ${
                  selectedDoc.id === doc.id
                    ? 'bg-cyan-600 text-white font-bold shadow glow-cyan'
                    : 'bg-industrial-800 text-slate-300 hover:bg-industrial-700 border border-industrial-700'
                }`}
              >
                {doc.category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Dual-Pane Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Pane: Interactive Document Image & Bounding Box Viewer */}
        <div className="lg:col-span-6 glass-panel rounded-xl p-5 border border-industrial-700 space-y-4">
          <div className="flex items-center justify-between border-b border-industrial-800 pb-3">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Scan className="w-4 h-4 text-cyan-400" />
                Raw Scanned Document Preview (300 DPI)
              </h3>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                {selectedDoc.name}
              </p>
            </div>
            <span className="text-[10px] font-mono text-slate-400">Interactive Bounding Boxes</span>
          </div>

          {/* Simulated Document Canvas */}
          <div className="relative bg-slate-900 border-2 border-industrial-700 rounded-xl aspect-[4/3] flex flex-col justify-between p-6 overflow-hidden shadow-2xl">
            
            {/* Document Background Simulation */}
            <div className="absolute inset-0 bg-gradient-to-b from-slate-950/90 to-slate-900/90 opacity-95 pointer-events-none" />

            <div className="relative z-10 space-y-4">
              <div className="border-b border-slate-700 pb-2 flex items-center justify-between text-slate-400 text-[10px] font-mono">
                <span>REFINERY TECHNICAL ARCHIVE • AIRGAPPED INGEST</span>
                <span>{selectedDoc.documentType}</span>
              </div>

              <div className="p-4 rounded border border-slate-800 bg-slate-950/60 text-slate-300 font-mono text-xs leading-relaxed whitespace-pre-line">
                {selectedDoc.rawOcrSnippet}
              </div>
            </div>

            {/* Interactive Bounding Boxes Overlay */}
            <div className="absolute inset-0 z-20 pointer-events-auto">
              {selectedDoc.extractions.map((ext) => {
                const isActive = activeExtractionId === ext.id;
                const isFlagged = ext.status === 'flagged_review';
                const isManual = ext.status === 'manual_override';

                return (
                  <div
                    key={ext.id}
                    onClick={() => setActiveExtractionId(ext.id)}
                    style={{
                      left: `${ext.location.x}%`,
                      top: `${ext.location.y}%`,
                      width: `${ext.location.width}%`,
                      height: `${ext.location.height}%`,
                    }}
                    className={`absolute cursor-pointer rounded border-2 transition-all flex items-start justify-end p-1 ${
                      isActive
                        ? 'border-cyan-400 bg-cyan-400/20 shadow-lg glow-cyan scale-105 z-30'
                        : isManual
                        ? 'border-red-500 bg-red-500/15'
                        : isFlagged
                        ? 'border-amber-400 bg-amber-400/15'
                        : 'border-emerald-400/70 bg-emerald-400/10 hover:border-emerald-400'
                    }`}
                    title={`${ext.field} (Confidence: ${ext.confidence}%)`}
                  >
                    <span className={`text-[8px] font-mono px-1 rounded font-bold ${
                      isActive ? 'bg-cyan-500 text-black' : isFlagged ? 'bg-amber-500 text-black' : 'bg-emerald-500 text-black'
                    }`}>
                      {ext.confidence}%
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="relative z-10 text-[10px] font-mono text-slate-500 flex justify-between pt-2 border-t border-slate-800">
              <span>Bounding boxes generated by Qwen2.5-VL / PaddleOCR</span>
              <span>Click box to highlight structured value</span>
            </div>
          </div>

          {/* Untrusted Data Tag Notice */}
          <div className="p-3 rounded-lg bg-industrial-950 border border-industrial-800 space-y-1.5">
            <span className="text-[10px] uppercase font-mono text-slate-400 font-bold block flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
              Untrusted Data Envelope (`guardrails.py`)
            </span>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              All OCR and VLM outputs are passed into agent memory inside strictly demarcated <code className="text-cyan-300">&lt;untrusted_ocr_data&gt;</code> blocks. The planner is system-instructed to treat internal tokens as passive data, completely neutralizing prompt injection attempts.
            </p>
          </div>
        </div>

        {/* Right Pane: Structured Confidence-Flagged Extraction Table */}
        <div className="lg:col-span-6 glass-panel rounded-xl p-5 border border-industrial-700 space-y-4">
          <div className="flex items-center justify-between border-b border-industrial-800 pb-3">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Tag className="w-4 h-4 text-cyan-400" />
                Structured Field Extractions & Confidence Flags
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Low-confidence readings are visually flagged for human verification
              </p>
            </div>
            <span className="text-[10px] font-mono text-cyan-400">
              {selectedDoc.extractions.length} Fields Extracted
            </span>
          </div>

          {/* Fields List */}
          <div className="space-y-3">
            {selectedDoc.extractions.map((ext) => {
              const isActive = activeExtractionId === ext.id;
              const isFlagged = ext.status === 'flagged_review';
              const isManual = ext.status === 'manual_override';

              return (
                <div
                  key={ext.id}
                  onClick={() => setActiveExtractionId(ext.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isActive
                      ? 'bg-industrial-800 border-cyan-400 shadow-md'
                      : isManual
                      ? 'bg-red-950/20 border-red-500/50 hover:border-red-400'
                      : isFlagged
                      ? 'bg-amber-950/20 border-amber-500/50 hover:border-amber-400'
                      : 'bg-industrial-950/60 border-industrial-800 hover:border-industrial-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-400 block font-semibold">
                        {ext.field}
                      </span>
                      <strong className="text-xs font-mono text-slate-100 mt-0.5 block">
                        {ext.normalizedValue}
                      </strong>
                    </div>

                    <div className="text-right font-mono">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isManual
                          ? 'bg-red-950 text-red-300 border-red-800'
                          : isFlagged
                          ? 'bg-amber-950 text-amber-300 border-amber-800 animate-pulse'
                          : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                      }`}>
                        {ext.confidence}% {isManual ? 'THREAT BLOCKED' : isFlagged ? 'FLAGGED FOR REVIEW' : 'HIGH CONFIDENCE'}
                      </span>
                    </div>
                  </div>

                  <div className="mt-2 pt-2 border-t border-industrial-850 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span>Raw OCR: "{ext.rawText}"</span>
                    <span>Status: {ext.status}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Raw Tagged Envelope Visualizer */}
          <div className="space-y-1.5 pt-2">
            <span className="text-[10px] font-mono text-slate-400 uppercase font-bold block">
              Sanitized Envelope Passed to Planner Core:
            </span>
            <pre className="bg-industrial-950 p-3 rounded-lg border border-industrial-800 font-mono text-[11px] text-cyan-300/90 whitespace-pre overflow-x-auto">
              {selectedDoc.untrustedEnclosed}
            </pre>
          </div>

        </div>

      </div>

    </div>
  );
};
