"""Explicit-depth volumetric stock; no missing-value fill or depth extrapolation."""
import math


def water_storage_mm(percent,intervals,depth_cm):
    if len(percent)!=len(intervals) or not isinstance(depth_cm,(int,float)) or isinstance(depth_cm,bool) or not math.isfinite(depth_cm) or depth_cm<=0:
        raise ValueError('Equal value/interval counts and positive target depth required')
    position=0.;total=0.
    for value,(top,bottom) in zip(percent,intervals):
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in (top,bottom)) or top!=position or bottom<=top:
            raise ValueError('Ordered contiguous layers from surface required')
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or not 0<=value<=100:
            raise ValueError('Measured volumetric percent required; no missing fill')
        used=min(bottom,depth_cm)-top
        total+=value*.1*used
        if bottom>=depth_cm:return total
        position=bottom
    raise ValueError('Target depth exceeds supplied profile')
