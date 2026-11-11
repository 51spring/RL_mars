"""Depth coverage geometry only; never interpolates or assigns soil values."""
import math


def depth_coverage(measured,target):
    def checked(spans):
        result=[]
        for top,bottom in spans:
            if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in (top,bottom)) or top<0 or bottom<=top:
                raise ValueError('Finite positive-width nonnegative depth intervals required')
            result.append((float(top),float(bottom)))
        result.sort()
        if any(a[1]>b[0] for a,b in zip(result,result[1:])):raise ValueError('Overlapping depth intervals')
        return result
    measured=checked(measured);target=checked(target)
    if not target:raise ValueError('Target intervals required')
    rows=[]
    for top,bottom in target:
        segments=[(max(top,a),min(bottom,b)) for a,b in measured if min(bottom,b)>max(top,a)]
        gaps=[];cursor=top
        for a,b in segments:
            if a>cursor:gaps.append([cursor,a])
            cursor=b
        if cursor<bottom:gaps.append([cursor,bottom])
        covered=math.fsum(b-a for a,b in segments)
        rows.append(dict(top_cm=top,bottom_cm=bottom,covered_cm=covered,
            fraction=covered/(bottom-top),missing_intervals_cm=gaps,
            fully_covered=not gaps,soil_values_assigned=False))
    return rows
