/**
@ This is for (3, 1) - sss scheme
@ Computing B'_d in SSS-based masking
@ Wei Cheng, 17-08-2020
**/

GF_K<alpha> := GF(2^8);

j := 72;
k := 80;
C := LinearCode<GF_K, 3|[1, 1, 1]>;
D := LinearCode<GF_K, 3|[1, alpha^j, alpha^k]>;
						  
C_dual_b := SubfieldRepresentationCode(Dual(C), GF(2));
D_dual_b := SubfieldRepresentationCode(Dual(D), GF(2));
d_dual := MinimumWeight(D_dual_b);

X_s := [x: x in D_dual_b | (x notin C_dual_b) and (Weight(x) eq d_dual)];
B_d_p := [[x,y]: x in X_s, y in X_s | x+y in C_dual_b];

print "D_dual_b: ", D_dual_b;
print "Weight distribution: ", WeightDistribution(D_dual_b);
print "d_dual: ", d_dual; // dual distance of D
print "B'_d: ", #B_d_p; // Number of codewords satisfy all conditions
print "Codewords: ", B_d_p; // Output all combinations of (x, y)
