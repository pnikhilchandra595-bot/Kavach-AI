import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  ShieldAlert, 
  FileEdit, 
  Lock, 
  Fingerprint, 
  UserCheck, 
  Users, 
  ShieldCheck 
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';

export const ApprovalGateModal: React.FC = () => {
  const { 
    approvalGateOpen, 
    setApprovalGateOpen, 
    activeScenario, 
    handleApproval,
    operatorRbac,
    twoPersonApproval,
    signPrimaryApproval,
    signSecondaryApproval
  } = useWorkbench();

  const [operatorNote, setOperatorNote] = useState(
    'Reviewed ultrasonic thickness profile and API 510 remaining life calculation. Confirmed Tray 14 minimum residual thickness at 7.82mm. Approved for 18-month reduced turnaround cycle.'
  );
  const [managerPin, setManagerPin] = useState('MRPL-OP-882');

  if (!approvalGateOpen || !activeScenario.approvalDetails) return null;

  const details = activeScenario.approvalDetails;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-industrial-900 border border-amber-500/60 rounded-xl shadow-2xl max-w-2xl w-full text-slate-100 overflow-hidden glow-amber animate-in fade-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="bg-amber-500/10 border-b border-amber-500/30 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-amber-300 tracking-wide">
                  HUMAN-IN-THE-LOOP APPROVAL GATE
                </h3>
                <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
                  {details.severity} SEVERITY
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Mandatory checkpoint before irreversible refinery action or document filing
              </p>
            </div>
          </div>

          <button
            onClick={() => setApprovalGateOpen(false)}
            className="text-slate-400 hover:text-slate-200 text-lg p-1"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 text-xs font-sans">
          
          {/* RBAC Operator Status Banner */}
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono">
            <div className="flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">Current Session RBAC:</span>
              <strong className="text-cyan-300">{operatorRbac.currentUser}</strong>
              <span className="text-slate-500">({operatorRbac.currentRole})</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              {operatorRbac.accessTier}
            </span>
          </div>

          {/* TWO-PERSON SUPERVISOR SIGN-OFF REQUIREMENT */}
          <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-amber-300 uppercase flex items-center gap-2">
                <Users className="w-4 h-4 text-amber-400" />
                Two-Person Supervisor Approval Mandate
              </span>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                OISD-105 / MRPL PSM COMPLIANT
              </span>
            </div>

            <p className="text-[11px] text-slate-300 leading-relaxed">
              This document alters the equipment inspection cadence in Crude Distillation Unit-II. To prevent unilateral modification of safety-critical refinery baselines, both the Technical Inspector and Plant Operations Manager must sign off.
            </p>

            {/* Checkpoints Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="bg-industrial-950 p-3 rounded-lg border border-emerald-500/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] uppercase font-mono text-slate-400 block font-bold">Primary Sign-Off (Technical)</span>
                  <span className="text-xs font-semibold text-slate-200">M. Sharma (NDT Level III)</span>
                  <span className="text-[10px] font-mono text-slate-500 block mt-0.5">Role: Chief Plant Inspector</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] font-mono font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> SIGNED
                </span>
              </div>

              <div className="bg-industrial-950 p-3 rounded-lg border border-amber-500/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] uppercase font-mono text-slate-400 block font-bold">Secondary Countersignature</span>
                  <span className="text-xs font-semibold text-amber-300">Operations Manager (MRPL-OP)</span>
                  <span className="text-[10px] font-mono text-slate-500 block mt-0.5">Role: Refinery Operations Lead</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 text-[10px] font-mono font-bold animate-pulse">
                  PENDING
                </span>
              </div>
            </div>
          </div>

          {/* Action Overview Card */}
          <div className="bg-industrial-850 rounded-lg p-4 border border-industrial-700 space-y-2.5">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-slate-400 block uppercase font-mono text-[10px] tracking-wider">Proposed Industrial Action</span>
                <strong className="text-sm font-semibold text-slate-200">{details.actionTitle}</strong>
              </div>
              <span className="text-[11px] font-mono px-2 py-1 rounded bg-industrial-800 text-cyan-300 border border-industrial-600">
                Target: {details.targetPath.split('/').pop()}
              </span>
            </div>

            <p className="text-slate-300 leading-relaxed bg-industrial-950/60 p-3 rounded border border-industrial-800 font-mono text-[11px]">
              {details.diffSummary}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-[11px]">
              <div>
                <span className="text-slate-400 block font-mono text-[10px]">AFFECTED RESOURCE</span>
                <span className="text-slate-200 font-medium">{details.affectedResource}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-mono text-[10px]">MANDATORY SIGN-OFF ROLE</span>
                <span className="text-amber-400 font-medium">{details.operatorRequiredRole}</span>
              </div>
            </div>
          </div>

          {/* Cryptographic Execution Hash */}
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800 flex items-center justify-between text-slate-400 font-mono text-[11px]">
            <div className="flex items-center gap-2">
              <Fingerprint className="w-4 h-4 text-cyan-400" />
              <span>Safety Cryptographic Hash:</span>
            </div>
            <span className="text-cyan-300 truncate max-w-xs">{details.safetyHash}</span>
          </div>

          {/* Supervisor Input */}
          <div className="space-y-2">
            <label className="block text-slate-300 font-medium text-xs">
              Operations Supervisor Verification Statement:
            </label>
            <textarea
              value={operatorNote}
              onChange={(e) => setOperatorNote(e.target.value)}
              rows={2}
              className="w-full bg-industrial-800 border border-industrial-700 rounded-lg p-2.5 text-slate-200 text-xs font-mono focus:ring-1 focus:ring-amber-400 outline-none"
            />

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Lock className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-slate-400 text-xs font-mono">Secondary Approver Digital PIN:</span>
              </div>
              <input
                type="text"
                value={managerPin}
                onChange={(e) => setManagerPin(e.target.value)}
                className="bg-industrial-800 border border-industrial-700 rounded px-2.5 py-1 text-slate-200 text-xs font-mono w-32 focus:ring-1 focus:ring-amber-400 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="bg-industrial-950 px-6 py-4 border-t border-industrial-800 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={() => handleApproval('REJECTED')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-950/80 hover:bg-red-900 text-red-300 border border-red-700 font-medium text-xs transition"
          >
            <XCircle className="w-4 h-4" />
            <span>REJECT & TERMINATE ACTION</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleApproval('MODIFIED')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-200 border border-industrial-600 font-medium text-xs transition"
            >
              <FileEdit className="w-4 h-4 text-cyan-400" />
              <span>Modify Parameters</span>
            </button>

            <button
              onClick={() => handleApproval('APPROVED')}
              className="flex items-center gap-1.5 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow glow-emerald transition"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>AUTHORIZE & COMMIT WRITE (2-PERSON SIGNED)</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
