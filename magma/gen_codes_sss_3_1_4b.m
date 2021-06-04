/**
@ generating linear codes for (3, 1) - SSS-based masking scheme on 4-bit variables
@ Wei Cheng, 26-08-2020
**/

P<X>:=IrreduciblePolynomial(GF(2),4);
//P<X>:= X^4 + X + 1;
print "Irreducible Polynomial P<X> = ", P;
GF16<X> := ext<GF(2)|P>;

print "\n--------------------- Random test on (3, 1)-SSS -----------------------";
for j:= 1 to 13 do
	for k:= j+1 to 14 do
		print "j, k = ", j, k;    
		G_1 := Matrix(GF16, 1, 3, [ 1, 1, 1]);   
		H_1 := Matrix(GF16, 1, 3, [ 1, X^j, X^k]);
		C_1 := LinearCode(G_1);  
		D_1 := LinearCode(H_1); 
		print "Dimension: ", Dimension(C_1 + D_1);
		//C_1;
		//print "Orig code D: ", (D_1); 
		print "WD orig D (word): ", WeightDistribution(D_1);
		//print "WD orig D  (bit): ", WeightDistribution(SubfieldRepresentationCode((D_1), GF(2)));
		//WeightDistribution(SubfieldRepresentationCode((D_1), GF(2)));     
		//print "Dual code: ", Dual(D_1);   
		//SubfieldRepresentationCode(Dual(D_1), GF(2, 1));   
		print "WD dual D (word): ", WeightDistribution(Dual(D_1)); 
		print "WD dual D  (bit): ", WeightDistribution(Dual(SubfieldRepresentationCode(D_1, GF(2))));
	end for;
end for;

exit;
