import os

CORPUS_DIR = r"c:\Users\DELL\Documents\SIH\knowledge_base\synthetic_corpus"
os.makedirs(CORPUS_DIR, exist_ok=True)

docs = {
    "MRPL-SOP-COR-301_Corrosion_Monitoring_Probes.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Standard Operating Procedure: Online Corrosion Monitoring & Electrical Resistance (ER) Probes
**Document Code:** MRPL-SOP-COR-301  
**Revision:** 2.4  
**Effective Date:** 2025-11-18  
**Refinery Unit:** CDU / VDU Overhead Systems  
**Target Equipment:** Overhead Vapor Condensers & Run-down Lines

---

### Section 1: Scope & Monitoring Technology
This document governs real-time corrosion rate monitoring across CDU-II atmospheric overhead condenser lines using flush-mounted Electrical Resistance (ER) probes and weight-loss coupon racks. The objective is to detect active ammonium chloride ($NH_4Cl$) and hydrochloric acid ($HCl$) dew-point corrosion before wall loss exceeds safety thresholds.

### Section 2: Operating Baseline & Alarm Thresholds
1. **Nominal Allowable Corrosion Rate:** Baseline target is $\le 0.12\text{ mm/year}$ for carbon steel overhead piping.
2. **Elevated Corrosion Advisory:** An online reading between **0.15 mm/yr and 0.25 mm/yr** triggers an advisory requiring optimization of neutralizing amine injection rate at quench pump P-105A.
3. **Critical High Corrosion Alarm:** Any persistent rate exceeding **0.30 mm/year** for $> 48\text{ hours}$ mandates immediate ultrasonic grid scanning of downstream elbows and salt deposition wash water rate increase to 8.0% of total crude volume.

### Section 3: ER Probe Calibration & Coupon Retrieval
1. ER probe digital transmitters (CR-101A through CR-108B) must be zero-referenced every 30 days.
2. Corrosion coupons must be removed under online hot-tap retraction protocols every 90 days, solvent cleaned per ASTM G1, and weighed to $\pm 0.1\text{ mg}$ precision to calculate verified metal loss.
""",

    "MRPL-MAN-HEX-220_Heat_Exchanger_Bundle_Service.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Equipment Maintenance Manual: Shell & Tube Heat Exchanger Bundle Servicing (E-104 Series)
**Document Code:** MRPL-MAN-HEX-220  
**Revision:** 3.0  
**Effective Date:** 2025-08-14  
**Refinery Unit:** Naphtha Hydrotreater (NHT) / CDU Heat Integration Train  
**Governing Standard:** TEMA Class R / API 660

---

### Section 1: Bundle Pulling & High-Pressure Hydro-Jetting
1. Prior to pulling tube bundles for Exchangers E-104A/B/C/D, positive blinding of both shell-side (gas oil) and tube-side (crude) must be verified.
2. Internal bundle cleaning shall be executed using automated high-pressure hydro-jetting machines operating at 1,000 to 1,200 bar water pressure with rotating sapphire nozzles.
3. All scale and sludge removed from bundle crevices must be tested for pyrophoric iron sulfide ($FeS$) and kept continuously wetted until safely neutralized.

### Section 2: Maximum Allowable Tube Plugging Criteria
1. When eddy current testing (ECT) reveals tube wall thinning exceeding 60% of original nominal gauge (0.80 mm residual on 14 BWG tubes), tubes must be plugged using tapered brass or stainless steel mechanical plugs.
2. **Plugging Ceiling:** The maximum allowable cumulative plugged tubes across any individual bundle in the E-104 train is **10.0% of total bundle tube count** (i.e. maximum 64 tubes out of 640 total tubes).
3. If tube plugging reaches or exceeds 10.0%, full re-tubing or bundle replacement must be procured and scheduled for the subsequent turnaround to prevent thermal duty starvation.

### Section 3: Hydrostatic Re-testing Protocol
Following reassembly with fresh spiral-wound 316L graphite-filled gaskets:
1. Shell-side hydrostatic test pressure: **1.50 times design MAWP** (18.0 bar gauge test pressure for 12.0 bar design).
2. Tube-side hydrostatic test pressure: **1.50 times design MAWP** (24.0 bar gauge test pressure for 16.0 bar design).
3. Test duration: Minimum 60 minutes hold time with zero pressure drop and zero visual seepage at tube-to-tubesheet rolled seal welds.
""",

    "MRPL-MAN-PMP-112_Centrifugal_Pump_Vibration_Limits.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Machinery Manual: API 610 Centrifugal Process Pumps Vibration & Mechanical Seal Limits
**Document Code:** MRPL-MAN-PMP-112  
**Revision:** 4.1  
**Effective Date:** 2026-02-05  
**Refinery Unit:** Process Units Wide / Machinery Maintenance Section  
**Governing Standard:** API 610 11th Edition / ISO 10816-3 Class I & II

---

### Section 1: Vibration Velocity Baselines & Trip Setpoints
This specification applies to all critical hydrocarbon pumps including Crude Bottoms Pumps P-101A/B and Reactor Feed Pumps P-201A/B.
1. **Normal Operational Vibration (Zone A/B):** Overall vibration velocity $\le 3.0\text{ mm/s RMS}$ measured at bearing housings.
2. **Alert / Advisory Threshold (Zone C):** Vibration velocity between **4.5 mm/s and 7.1 mm/s RMS**. Mandates daily spectral FFT vibration monitoring to detect unbalance, bearing race spalling, or cavitation.
3. **Automatic Machine Trip (Zone D):** Vibration exceeding **9.0 mm/s RMS** or bearing peak acceleration $> 3.5\text{ g pk-pk}$ mandates immediate trip and changeover to the standby auxiliary pump.

### Section 2: Bearing Temperature Limits
1. Maximum allowable steady-state hydrodynamic bearing metal temperature is **95 °C**.
2. Alert threshold: **85 °C**.
3. Bearing cooling water return temperature shall not exceed **55 °C** with a minimum flow rate of 15 liters/minute.

### Section 3: Dual Mechanical Seal Barrier Fluid Requirements
1. Process pumps handling hydrocarbons above auto-ignition temperature (250 °C) or volatile light ends must feature Plan 53B dual pressurized mechanical seals.
2. **Seal Barrier Oil Pressure:** Must be maintained at a minimum of **1.5 bar above maximum seal chamber pressure**, and never lower than **4.0 bar(g)** absolute.
3. A drop in seal barrier accumulator level $> 0.5\text{ liters/24 hours}$ indicates primary seal face leakage and requires maintenance inspection.
""",

    "MRPL-STD-API-510_Pressure_Vessel_RUL_Calculation.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Engineering Standard: In-Service Pressure Vessel Inspection & Remaining Life Calculation
**Document Code:** MRPL-STD-API-510  
**Revision:** 5.0  
**Effective Date:** 2025-09-30  
**Refinery Unit:** Inspection Department  
**Governing Code:** API 510 10th Edition / ASME Section VIII Division 1

---

### Section 1: Governing Remaining Useful Life (RUL) Equation
Remaining service life of in-service pressure vessels, columns, and drums shall be computed per API 510 Section 7.1.1:
$$\text{Remaining Life (Years)} = \frac{t_{\text{actual}} - t_{\text{required}}}{\text{Corrosion Rate}}$$
Where:
- $t_{\text{actual}}$: The actual thickness in millimeters measured at the most severely thinned structural sector.
- $t_{\text{required}}$: The minimum allowable thickness computed in accordance with original design construction code without corrosion allowance.
- $\text{Corrosion Rate}$: Determined as the conservative maximum of either long-term rate ($C_{LT}$) or short-term rate ($C_{ST}$).

### Section 2: Long-Term vs Short-Term Corrosion Rate
1. **Long-Term Rate ($C_{LT}$):**
   $$C_{LT} = \frac{t_{\text{initial}} - t_{\text{actual}}}{\text{Years between baseline commissioning and current inspection}}$$
2. **Short-Term Rate ($C_{ST}$):**
   $$C_{ST} = \frac{t_{\text{previous}} - t_{\text{actual}}}{\text{Years between previous turnaround and current inspection}}$$
3. If $C_{ST} > 1.5 \times C_{LT}$, process operational conditions (e.g. higher sour crude feed sulfur or chloride excursion) have accelerated metal loss; $C_{ST}$ must be adopted for RUL and inspection interval reduction.

### Section 3: MAWP Derating Protocol
When actual wall thickness approaches $t_{\text{required}}$ and replacement is deferred:
1. Maximum Allowable Working Pressure (MAWP) must be officially derated in refinery vessel database using:
   $$P_{\text{derated}} = \frac{S \times E \times t_{\text{actual}}}{R + 0.6 \times t_{\text{actual}}}$$
2. Pressure safety valve (PSV) setpoints must be recalibrated downward to match $P_{\text{derated}}$ prior to vessel repressurization.
""",

    "MRPL-STD-ASME-VIII_Shell_Thickness_Design_Formulae.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Technical Standard: Cylindrical Shell Thickness & Stress Equations per ASME Section VIII
**Document Code:** MRPL-STD-ASME-VIII  
**Revision:** 4.0  
**Effective Date:** 2025-06-15  
**Refinery Unit:** Technical Services & Pressure Vessel Engineering  
**Governing Code:** ASME Boiler & Pressure Vessel Code Section VIII Division 1 (Part UG-27)

---

### Section 1: Cylindrical Shell Circumferential Stress Equation
For cylindrical shells under internal pressure, the required wall thickness $t$ for circumferential stress (longitudinal joints) is calculated as:
$$t = \frac{P \times R}{S \times E - 0.6 \times P}$$
Where:
- $P$: Internal Design Pressure in MPa (or bar, converted consistently).
- $R$: Inside Radius of shell course before corrosion allowance, in mm.
- $S$: Maximum allowable stress value of material at design temperature per ASME Section II Part D, in MPa.
- $E$: Joint efficiency of category A and B welds (typically $E = 1.00$ for 100% full radiography; $E = 0.85$ for spot radiography per UW-12).

### Section 2: Material Property Baselines for Refinery Steels
1. **SA-516 Grade 70 (Normalized):**
   - Tensile Strength: 485 MPa
   - Yield Strength: 260 MPa
   - Allowable Stress $S$ at 100 °C: 138.0 MPa
   - Allowable Stress $S$ at 350 °C: 118.0 MPa
2. **SA-387 Grade 11 Class 2 (1.25Cr-0.5Mo):**
   - Allowable Stress $S$ at 450 °C: 112.0 MPa
3. **SA-240 Type 316L Stainless Steel:**
   - Allowable Stress $S$ at 200 °C: 115.0 MPa

### Section 3: Longitudinal Stress Verification
Circumferential joints must satisfy longitudinal stress requirements:
$$t_{long} = \frac{P \times R}{2 \times S \times E + 0.4 \times P}$$
Since circumferential stress dictates higher thickness, the circumferential equation governs minimum required plate specification.
""",

    "MRPL-SOP-TNK-501_Tank_Farm_Hydrocarbon_Transfer.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Standard Operating Procedure: Tank Farm Crude Oil Receipt & High-High Level Safety
**Document Code:** MRPL-SOP-TNK-501  
**Revision:** 3.3  
**Effective Date:** 2026-02-28  
**Refinery Unit:** Oil Movement & Storage (OM&S) / Tank Farm  
**Target Equipment:** Floating Roof Crude Storage Tanks (TK-501 through TK-508)

---

### Section 1: Single Point Mooring (SPM) Pipeline Receipt Lineup
1. Confirm positive alignment of 48" subsea crude receipt line from Mangalore SPM to designated target tank TK-502.
2. Verify electrostatic grounding clamp resistance is $< 10.0\ \Omega$ before opening motorized gate valve MOV-5021.
3. Initial line filling velocity must not exceed **1.0 m/s** until floating roof lands off legs and starts floating (minimum 1.8 meters liquid level) to prevent static charge accumulation.

### Section 2: Overfill Protection & Radar Gauging
1. Tank levels must be redundantly tracked via Servo Gauge (LT-502A) and independent Non-Contact Radar Gauge (LT-502B).
2. **Safe Fill Level (90% capacity):** Normal automated receipt shutoff setpoint.
3. **High Level Alarm (HLA, 92% capacity):** Visual and audible strobe alert in Tank Farm Control Room.
4. **Independent High-High Level Switch (LSHH, 95% capacity):** SIL-2 rated tuning-fork level switch initiates automatic slam-shut of inlet emergency isolation valve (EIV-502) within 15 seconds, independent of DCS control.
""",

    "MRPL-CORR-2026-08_Inspector_Turnaround_Brief.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Technical Memorandum: Turnaround Inspection Summary & RUL Advisory for Column CRU-C-101
**Document Code:** MRPL-CORR-2026-08  
**Date:** 2026-08-30  
**From:** Chief Plant Inspector (NDT Level III), Inspection Department  
**To:** Operations Manager, Crude Distillation Unit - II  
**Subject:** UT Scanning Findings on Tray 14 Shell Course of Column CRU-C-101

---

### Executive Brief
During the scheduled turnaround NDT examination of Atmospheric Column CRU-C-101 on August 29, 2026, localized wall thinning was detected in the intermediate shell course around Tray 14 elevation. 

Key quantitative findings:
1. **Measured Minimum Residual Thickness:** **7.82 mm** recorded at $180^\circ$ quadrant elevation (nominal design was 10.00 mm).
2. **Governing Retirement Thickness ($t_{min}$):** **6.20 mm** per ASME Section VIII and MRPL-SOP-CRU-402 Rev 4.
3. **Remaining Useful Life (RUL):** Calculated at **7.36 years** at the localized corrosion rate of 0.22 mm/year.
4. **Mandatory Procedural Action:** Because measured thickness is below the 8.00 mm threshold specified in MRPL-SOP-CRU-402 Section 4.2, the turnaround inspection interval must be officially reduced from 36 months to **18 months**.

### Action Item for Operations
Please endorse the attached formal Technical Approval Note (`MRPL_Approval_Note_CRU_C101_2026.docx`) to update the refinery asset integrity database and authorize unit startup.
""",

    "MRPL-SOP-FLR-001_Flare_Knockout_Drum_Purging.md": """# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Standard Operating Procedure: Refinery Flare Header Sweep & Liquid Knockout Drum Management
**Document Code:** MRPL-SOP-FLR-001  
**Revision:** 4.0  
**Effective Date:** 2025-12-01  
**Refinery Unit:** Utilities & Offsites / Flare System  
**Target Equipment:** Flare Knockout Drums V-701 (High Pressure) and V-702 (Low Pressure)

---

### Section 1: Continuous Purge Gas Flow Requirements
1. To prevent air ingress and flashback into the 42" flare header, a continuous nitrogen or fuel gas purge must be maintained.
2. Minimum header sweep purge velocity: **0.15 m/s** under all ambient conditions.
3. Oxygen analyzer at flare stack base (AI-701) must alarm at $> 0.5\%\text{ vol } O_2$ and trip supplemental sweep gas if $> 1.0\%\text{ vol } O_2$.

### Section 2: Knockout Drum Liquid Pumping & High Level Trip
1. Hydrocarbon condensates in Knockout Drum V-701 must be pumped continuously to slop oil tanks via auto-start pumps P-701A/B.
2. **High Level Trip:** If liquid level reaches 70% in Drum V-701, an automated interlock alarm sounds in all central control rooms.
3. If liquid reaches 85%, unit feed rates across CDU and HCU must be reduced by 30% immediately to prevent hydrocarbon liquid carryover to the flare tip.
"""
}

for filename, content in docs.items():
    filepath = os.path.join(CORPUS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Written: {filename} ({len(content)} bytes)")

print("\nSuccessfully generated all synthetic corpus documents!")
