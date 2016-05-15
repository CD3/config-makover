
def close( a, b, tol = 0.001 ):
    '''Return true if a and b are with tol of each other (tol is a fraction)'''
    a = float(a)
    b = float(b)
    return (a - b)**2 < 4*tol*tol*(a**2 + b**2)

Close = close
