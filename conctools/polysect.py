'''

This module contains code related to polygon shaped reinforced concrete sections.


'''


def polygon_area(xv, yv, signed=False):
    ''' Return the area of a non-self-intersecting polygon given the coordinates of its vertices'''

    # Perform shoelace multiplication
    a1 = [xv[i] * yv[i+1] for i in range(len(xv)-1)]
    a2 = [yv[i] * xv[i+1] for i in range(len(yv)-1)]

    # Check if area should be signed and return area
    if signed:          # <--- Same as "if signed == True:"
        return 1/2 * (sum(a1) - sum(a2))
    else:
        return 1/2 * abs(sum(a1) - sum(a2))


def polygon_centroid(x, y):

    # Initialize empty lists for holding summation terms
    cx, cy = [], []
    
    # Loop over vertices and put the summation terms in the lists
    for i in range(len(x)-1):
        
        # Compute and append summation terms to each list
        cx.append((x[i] + x[i+1]) * (x[i] * y[i+1] - x[i+1] * y[i]))
        cy.append((y[i] + y[i+1]) * (x[i] * y[i+1] - x[i+1] * y[i]))

    # Calculate the signed polygon area by calling already defined function
    A = polygon_area(x, y, signed=True)    
        
    # Sum summation terms and divide by 6A to get coordinates
    Cx = sum(cx) / (6*A)
    Cy = sum(cy) / (6*A)
    
    return Cx, Cy  
