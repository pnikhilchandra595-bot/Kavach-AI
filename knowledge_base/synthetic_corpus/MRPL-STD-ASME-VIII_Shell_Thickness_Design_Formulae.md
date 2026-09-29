# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
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
$$t = rac{P 	imes R}{S 	imes E - 0.6 	imes P}$$
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
$$t_{long} = rac{P 	imes R}{2 	imes S 	imes E + 0.4 	imes P}$$
Since circumferential stress dictates higher thickness, the circumferential equation governs minimum required plate specification.
