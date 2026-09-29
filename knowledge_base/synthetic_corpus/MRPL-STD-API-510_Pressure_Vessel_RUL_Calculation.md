# [SYNTHETIC REPRESENTATIVE CORPUS — NOT OFFICIAL MRPL DATA]
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
$$	ext{Remaining Life (Years)} = rac{t_{	ext{actual}} - t_{	ext{required}}}{	ext{Corrosion Rate}}$$
Where:
- $t_{	ext{actual}}$: The actual thickness in millimeters measured at the most severely thinned structural sector.
- $t_{	ext{required}}$: The minimum allowable thickness computed in accordance with original design construction code without corrosion allowance.
- $	ext{Corrosion Rate}$: Determined as the conservative maximum of either long-term rate ($C_{LT}$) or short-term rate ($C_{ST}$).

### Section 2: Long-Term vs Short-Term Corrosion Rate
1. **Long-Term Rate ($C_{LT}$):**
   $$C_{LT} = rac{t_{	ext{initial}} - t_{	ext{actual}}}{	ext{Years between baseline commissioning and current inspection}}$$
2. **Short-Term Rate ($C_{ST}$):**
   $$C_{ST} = rac{t_{	ext{previous}} - t_{	ext{actual}}}{	ext{Years between previous turnaround and current inspection}}$$
3. If $C_{ST} > 1.5 	imes C_{LT}$, process operational conditions (e.g. higher sour crude feed sulfur or chloride excursion) have accelerated metal loss; $C_{ST}$ must be adopted for RUL and inspection interval reduction.

### Section 3: MAWP Derating Protocol
When actual wall thickness approaches $t_{	ext{required}}$ and replacement is deferred:
1. Maximum Allowable Working Pressure (MAWP) must be officially derated in refinery vessel database using:
   $$P_{	ext{derated}} = rac{S 	imes E 	imes t_{	ext{actual}}}{R + 0.6 	imes t_{	ext{actual}}}$$
2. Pressure safety valve (PSV) setpoints must be recalibrated downward to match $P_{	ext{derated}}$ prior to vessel repressurization.
