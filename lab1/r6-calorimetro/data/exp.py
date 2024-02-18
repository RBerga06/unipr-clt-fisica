from rberga06.phylab import Datum
q = Datum(87.288, 0.007)
k = Datum(-0.004796, 4e-6)

t = -1/k
print(t)

#          - t / tau
#  y = A e
#
#         kt + q      k t       q       q      - t / (-1/k)
#  y = e          = e       · e    =  e   ·  e

# A = exp(q)
# tau = -1/k
