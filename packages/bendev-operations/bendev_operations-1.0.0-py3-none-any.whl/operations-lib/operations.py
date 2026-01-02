# geometirc,g
def csq(a,b,c):
    try:
        final = -b / (2*a)
        det = b**2 - 4*a*c
        x = (-(b)+(det**0.5)) / (2*a)
        y = (-(b)-(det**0.5)) / (2*a)
        if det < 0:
            return "Not Expressible"
        elif det > 0:
            return f"{x} , {y}"
        else:
            return final
    except ValueError as e:
        return f"Integer or Flaot error {e}!"
# Areas,v
def rhom(a,b,h):
    result = (h/2)*(a+b)
    return result

def rsquare(r):
    try:
        result = (22/7) * r**2
        return result
    except ValueError:
        return "Integer or Flaot error!"
    
    
def rsquare(d):
    try:
        result = (22/7) * (d/2)**2
        return result
    except ValueError:
        return "Integer or Flaot error!"
    


# volumes,v
def cuboid(r,h):
    result = (22/7) * r**2 *h
    return result
# general
def reverse(value):
    expect = ""
    if type(value) == int:
        expect = str(value)
    else:
        expect = value
    return expect[::-1]

def length(string):
    count = 0
    for char in string:
        if char:
            count += 1
    return count

# physics,p
    