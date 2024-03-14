from typing import List, Dict, Tuple
from .api import fetch_trends_dataA, fetch_trends_dataB

# def __quantify_trend(counts: List[int]) -> float: 
#     x = np.arange(0, len(counts))
#     y = np.array(counts)
#     z = np.polyfit(x, y, 2)
#     return z[0]

# def batch_trends(data: List[Tuple[int, List[int]]]) -> Dict[int: int]: 
#     result = {}
#     for d in data:
#         result[d[0]] = __quantify_trend(d[1])
#     return result

# def get_top_trends(percent: float, trends: Dict[int: int]) -> List[int]: 
#     sort = {k: v for k, v in sorted(trends.items(), key=lambda item: item[1], reverse=True)}
#     result = []
#     i = len(sort)
#     for k in sort:
#         if i < int(len(sort)*percent):
#             break
#         if k not in result:
#             result.append(k)
#         i -= 1
#     return result

def compute_trends(prod_prob_countsA, prod_prob_countsB):
    # Get top 5 product problems
    prod_prob_countsC = prod_prob_countsA
    for p, v in prod_prob_countsB.items():
        if p in prod_prob_countsC:
            prod_prob_countsC[p] += v
        else:
            prod_prob_countsC[p] = v
    prod_prob_countsC = {k: v for k, v in sorted(prod_prob_countsC.items(), key=lambda item: item[1], reverse=True)}
    top = {}
    for _, k in zip(range(5), prod_prob_countsC):
        top[k] = prod_prob_countsC[k]
    
    # compute ratios
    qs = {}
    for p, c in top.items():
        p1a = prod_prob_countsA[p]
        np1a = sum(prod_prob_countsA.values()) - prod_prob_countsA[p]
        ra = p1a/np1a + 0.025
        p1b = prod_prob_countsB.get(p, 1)
        np1b = sum(prod_prob_countsB.values()) - prod_prob_countsB.get(p, 1)
        rb = p1b/np1b
        if ra > rb:
            q = ra - rb
            qs[p] = q
    
    # get top 3 product problems ratios
    qs = {k: v for k, v in sorted(qs.items(), key=lambda item: item[1], reverse=True)}

    top3 = []
    i = 0
    for p in qs.keys():
        if i >= 3:
            break
        top3.append(p)
        i += 1
    
    return top3
    
def fetch_trends():
    return compute_trends(fetch_trends_dataA(), fetch_trends_dataB())
