/**
@ This is for (3, 1) - sss scheme
@ Computing B'_d in SSS-based masking
@ Wei Cheng, 17-08-2020
**/

GF256<alpha> := GF(2^8);

C := LinearCode<GF256, 3|[1, 1, 1]>;
D := LinearCode<GF256, 3|[alpha, alpha^73, alpha^81]>;

C_dual_b := SubfieldRepresentationCode(Dual(C), GF(2));
D_dual_b := SubfieldRepresentationCode(Dual(D), GF(2));
d_dual := MinimumWeight(D_dual_b);

CWs := [[x, x+a]: x in D_dual_b, a in (D_dual_b meet C_dual_b) | (x+a in D_dual_b) and (Weight(x) eq d_dual) and (Weight(x+a) eq d_dual)];

print "B'_d: ", #CWs; // Number of codewords satisfy all conditions
print "Codewords: ", CWs; // Output all combinations of (x, y)
