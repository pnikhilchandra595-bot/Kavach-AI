# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
# Mangalore Refinery and Petrochemicals Limited (MRPL)
## Standard Operating Procedure: Crude Distillation Column Shell Inspection & Retirement Thresholds
**Document Code:** MRPL-SOP-CRU-402  
**Revision:** 4.2  
**Effective Date:** 2026-03-15  
**Governing Standard:** API 510 / ASME Section VIII Div 1  
**Refinery Unit:** Crude Distillation Unit - II (CDU-II)  
**Target Equipment:** Column CRU-C-101 (Atmospheric Fractionator)

---

### Section 1: Purpose & Applicability
This procedure governs non-destructive examination (NDE) and ultrasonic thickness (UT) evaluation for the intermediate and bottom shell courses of Atmospheric Crude Distillation Column CRU-C-101. It specifies mandatory retirement thresholds, corrosion rate governing equations, and criteria triggering emergency reduction of turnaround intervals.

### Section 2: Design Specifications & Baseline Metallurgy
- **Vessel Tag:** CRU-C-101
- **Design Pressure (MAWP):** 15.2 bar (gauge) at top vapor space; 18.5 bar (gauge) at bottom sump
- **Design Temperature:** 385 °C (flash zone); 165 °C (overhead)
- **Shell Metallurgy:** Carbon Steel SA-516 Grade 70 with 3.0 mm Monel 400 roll-clad internal lining on Trays 1 to 8; bare SA-516 Gr 70 on Trays 9 to 24
- **Nominal Shell Thickness ($t_{nom}$):** 10.00 mm (Intermediate shell courses, Trays 10–22)
- **Original Corrosion Allowance ($C_A$):** 3.80 mm

### Section 3: Ultrasonic Thickness (UT) Scanning Grid
1. Ultrasonic thickness measurements must be acquired using a calibrated dual-crystal probe operating at 5.0 MHz.
2. A minimum of 16 measurement points per tray elevation must be logged across 4 cardinal quadrants ($0^\circ, 90^\circ, 180^\circ, 270^\circ$).
3. Any reading with an acoustic coupling verification confidence index below 85% must be rescanned following solvent surface de-scaling.

### Section 4: Minimum Retirement Thickness Criteria
1. The absolute minimum retirement thickness ($t_{min}$) for the intermediate shell courses (Trays 10 to 22) is calculated as:
   $$t_{min} = \frac{P \times R}{S \times E - 0.6 \times P} = 6.20\text{ mm}$$
   including ASME Section VIII design margins.
2. **Mandatory Action Threshold:** When measured residual thickness at any elevation falls below **8.00 mm**, the baseline 36-month turnaround inspection cycle must be immediately halved to **18 months**.
3. If measured wall thickness decreases below 6.50 mm (within 5% of retirement limit), continuous online ultrasonic pulse-echo loggers must be welded at quadrant quadrants and logged every shift.

### Section 5: Corrosion Rate & Remaining Useful Life (RUL)
The remaining useful life (RUL) in years shall be determined by:
$$RUL = \frac{t_{actual} - t_{min}}{\text{Corrosion Rate}}$$
Where $\text{Corrosion Rate}$ is calculated as:
$$\text{Corrosion Rate} = \frac{t_{initial} - t_{actual}}{\Delta \text{Time in Service}}$$
Where $t_{initial} = 10.00\text{ mm}$ and measured service time is logged from turnaround baseline.

### Section 6: Human Sign-off & Filing Protocol
Any recommendation to reduce inspection intervals or operate with localized thinning requires formal plant sign-off:
1. Preparation of formal Technical Approval Note (`MRPL_Approval_Note_CRU_C101.docx`).
2. Review and digital countersignature by the Chief Plant Inspector (Level III NDT).
3. Final sign-off by the Plant Operations Manager prior to restart.
