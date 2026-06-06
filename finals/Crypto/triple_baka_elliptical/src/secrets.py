from sage.all import *


def get_triplet_special(G, order):
    R = Integers(order)
    
    i = R(-1).sqrt() 
    assert i**2 == -1

    inv3 = R(3).inverse()
    
    assert 3 * G * inv3 == G
    
    while True:
        u, v = R.random_element(), R.random_element()
        
        a = R(u**2 - v**2) 
        b = R(2*u*v)
        c = R(i * (u**2 + v**2))
        
        
        LHS = ((a**3 + b**3 + c**3) + (a+b+c) * (a*b + b*c + c*a)) * G * inv3
        RHS = a * b * c * G
        
        if LHS == RHS:
            return a, b, c

flag = b"ASRCTF{7r1n0m1al5_m3Ans_TR1pl3_tH3_b4k4!1!Il1!!}"
