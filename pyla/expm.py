from pyla.numeric_context import FloatContext
from pyla.core import solve, shape_mat, zeros, eye, mat_sum, mat_scale, mat_combine_inplace, mmul
from itertools import izip
""" Matrix exponent implementation, using order (q,q) pade approximations

Formulas taken from:
http://mathoverflow.net/questions/41226/pade-approximant-to-exponential-function
"""

#def _fac(n):
#    p = 1
#    for i in xrange(1, n+1):
#        p *= i
#    return p

def _exp_pade_coeffs( q, context=FloatContext ):
    """Coefficients of the qq pade approximation (numerator only)"""
    a0 = context.one
    aa = [a0]
    ai = a0
    for j in xrange(1, q+1):
        #ai = _fac(2*q-j)*_fac(q)/context.from_int( 
        #    _fac(2*q)*_fac(j)*_fac(q-j) )

        ai = ai * (q-j+1) / (2*q-j+1) / j 

        aa.append(ai)
    return aa

def matrix_powers(m):
    """Generates infinite sequence of matrix powers, starting from m^0"""
    yield eye(len(m)) # m^0
    yield m           # m^1 
    m_i = mmul( m, m )
    while True:
        yield m_i
        m_i = mmul( m_i, m )

def expm( m, context=FloatContext, order=7 ):
    """Matrix exponent, using Pade approximation of given order
    """
    a = _exp_pade_coeffs( order )
    n,n_ = shape_mat( m )
    assert( n == n_ )
    
    num = zeros(n,n)
    den = zeros(n,n)

    s = 1
    for m_i, ai in izip( matrix_powers(m), a ):
        mat_combine_inplace( num, m_i, ai )
        mat_combine_inplace( den, m_i, s*ai)
        s = -s

    return solve( den, num )
                             
def expms( m, context=FloatContext, order=7 ):
    """Calculate quickly exp(t*A), for different t.
    Takes matrix M and returns function f(t) = exp(t*M).
    
    Each call to that function requires no matrix multiplications and several additions
    """
    a = _exp_pade_coeffs( order )
    n,n_ = shape_mat( m )
    assert( n == n_ )
    
    #Prepare list of m powers and Pade coefficients
    m_a_list = zip( matrix_powers(m), a )

    def calculate_expm(t):
        num = zeros(n,n)
        den = zeros(n,n)
        s = 1
        k = context.one # t^n is stored here
        for m_i, ai in m_a_list:
            aik = ai*k
            mat_combine_inplace( num, m_i, aik )
            mat_combine_inplace( den, m_i, s*aik)
            s = -s
            k *= t
        return solve( den, num )
    return calculate_expm
