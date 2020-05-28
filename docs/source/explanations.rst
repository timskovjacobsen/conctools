
============
Explanations
============

Capacity diagram
****************

- Going from almost full tension to full tension

When the neutral axis is just inside the cross section, with tension dominating, i.e. only a very small compression zone, all rebars will most likely be in tension and yielding.

This is because the strain at the most compressed point has to be $\epsilon_cu=0.0035$. This makes the strain diagram have an extremely steep slope and thus, rebars don't have to be far away to be yielding.

The capacity diagram will then make a "spike" when the neutral axis moves just outside the cross section, as the point with failure strain now moves to be the rebar with highest strain, rather than the most compressed concrete point.
For this neutral axis location, the rebars closest to the neutral axis will most likely ***not*** be yielding, which makes the total force in all rebars drop suddenly from one point to the next.

Solution
********

Once the neutral axis moves beyond the section boundary in tension, move the neutral axis to +/- infinity (depending on which direction is full tension).
Thus, only a single calculation with full tension is considered.
The capacity diagram will still have points that are that are close to the uniform tension point so the curve looks smooth.
The reason for this is that the neutral axis location with very small tension zone is almost identical to that. The only difference being that a small concrete force is counteracting the fully tensioned rebars.

**Note:** The same is not true for the full compression here. Here, multiple points "should/could" be evaluated without getting such a spike. However, a small kink may occur as the uniform compression scenario has a significantly reduced failure strain (eps_cu vs eps_c).
