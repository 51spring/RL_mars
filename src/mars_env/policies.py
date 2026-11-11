"""Common feasible rule policies and the irrigation-only policy interface.

Thresholds must be selected on validation data; defaults are diagnostic only.
"""
from dataclasses import dataclass
import math
import gymnasium as gym
import numpy as np
from .observations import FIELDS, FRAME_SIZE, OBSERVATION_SIZE
from .resources import ResourceRules


def public_values(observation):
    obs=np.asarray(observation,dtype=float)
    if obs.shape!=(OBSERVATION_SIZE,) or not np.isfinite(obs).all():
        raise ValueError(f'Expected finite public {OBSERVATION_SIZE}-vector')
    return {name:float(value*scale) for (name,scale),value in zip(FIELDS,obs[-FRAME_SIZE:])}


@dataclass(frozen=True)
class NoInputPolicy:
    """Zero irrigation, fertilizer and spray under the common action contract."""
    def action(self,observation,mask,rules=None):
        public_values(observation)
        mask=np.asarray(mask,dtype=bool)
        if mask.shape!=(17,) or not all(mask[i] for i in (0,6,15)):
            raise ValueError('Zero action must be feasible')
        return np.zeros(3,dtype=np.int64)


@dataclass(frozen=True)
class RulePolicy:
    water_stress_threshold:float=.3
    irrigation_mm:float=10
    survey_threshold:float=.3
    baseline_nitrogen:tuple=((45,80),(65,54),(95,27))
    stage_water:tuple=()  # (istage, stress threshold, irrigation mm); other stages use the defaults above

    def __post_init__(self):
        if (not all(math.isfinite(x) for x in (self.water_stress_threshold,self.irrigation_mm,self.survey_threshold))
                or not 0<=self.water_stress_threshold<=1 or not 0<=self.survey_threshold<=1 or self.irrigation_mm<0):
            raise ValueError('Invalid rule thresholds')
        if any(not 0<=threshold<=1 or amount<0 for _,threshold,amount in self.stage_water):
            raise ValueError('Invalid stage irrigation rule')

    def water_request(self,values):
        stage=round(values['istage'])
        threshold,amount=next(((t,a) for s,t,a in self.stage_water if s==stage),
                              (self.water_stress_threshold,self.irrigation_mm))
        # swfac is the gym-DSSAT stress index (1 - native SWFAC).
        return amount if values['swfac']>=threshold else 0

    @classmethod
    def from_config(cls,config):
        return cls(**config['baseline_policy'],
                   baseline_nitrogen=tuple(sorted(config['management']['baseline_nitrogen'].items())))

    def action(self,observation,mask,rules=None):
        rules=rules or ResourceRules();values=public_values(observation);mask=np.asarray(mask,dtype=bool)
        if mask.shape!=(17,) or not mask[0] or not mask[6] or not mask[15]:raise ValueError('Invalid feasible mask')
        dap=int(round(values['dap']))
        desired_n=dict(self.baseline_nitrogen).get(dap,0)
        desired_w=self.water_request(values)
        water=max(i for i,x in enumerate(rules.water_grid) if x<=desired_w and mask[i])
        nitrogen=max(i for i,x in enumerate(rules.nitrogen_grid) if x<=desired_n and mask[6+i])
        # survey_value is 0 without a reading; thresholds are positive, so no reading never triggers a spray.
        spray=int(self.survey_threshold>0 and values['survey_value']>=self.survey_threshold and mask[16])
        return np.array([water,nitrogen,spray],dtype=np.int64)


@dataclass(frozen=True)
class ReductionResponseRule(RulePolicy):
    """b0': the rule policy until a reduction is known, then paced water with a flowering reserve.

    Applies only while the remaining water is below the rule's expected remaining demand
    (``remaining_demand_mm``: (day after planting, mm) knots); otherwise it acts as the rule.
    Before flowering only water above ``reserve_mm`` may be spent; from flowering through
    grain fill the whole remainder is available. Each pool is spread over the irrigation
    events expected before its window ends. The stress trigger itself is unchanged.
    """
    reserve_mm:float=0.
    flowering_day:int=0
    maturity_day:int=1
    event_interval_days:float=1.
    protected_stages:tuple=(4,5)
    remaining_demand_mm:tuple=()
    demand_margin:float=1.  # the reserve applies only below this share of the expected remaining demand

    @classmethod
    def from_config(cls,config):
        return cls(**config['baseline_policy'],**config['reduction_response_rule'],
                   baseline_nitrogen=tuple(sorted(config['management']['baseline_nitrogen'].items())))

    def action(self,observation,mask,rules=None):
        rules=rules or ResourceRules();base=super().action(observation,mask,rules);values=public_values(observation)
        if values['announced']<.5:return base
        left=values['water_left'];dap=values['dap'];mask=np.asarray(mask,dtype=bool)
        if self.remaining_demand_mm:
            days,demand=zip(*self.remaining_demand_mm)
            if left>=self.demand_margin*np.interp(dap,days,demand):return base
        if round(values['istage']) in self.protected_stages:pool,end=left,self.maturity_day
        else:pool,end=max(0.,left-self.reserve_mm),self.flowering_day
        events=max(1,math.ceil(max(1.,end-dap)/self.event_interval_days))
        allowance=pool/events if pool<=0 else max(pool/events,min(rules.water_grid[1],pool))
        desired=min(rules.water_grid[base[0]],allowance)+1e-6
        base[0]=max(i for i,x in enumerate(rules.water_grid) if x<=desired and mask[i])
        return base


CHANNEL_SLICES=(slice(0,6),slice(6,15),slice(15,17))
CHANNEL_SIZES=(6,9,2)


def channel_mask(mask,channels):
    return np.concatenate([np.asarray(mask,dtype=bool)[CHANNEL_SLICES[c]] for c in channels])


class FrozenChannels:
    """A fixed policy network answering for some channels from the current observation."""
    def __init__(self,model,channels,deterministic=True):
        self.model,self.channels,self.deterministic=model,tuple(channels),deterministic

    def apply(self,observation,mask,action):
        predicted,_=self.model.predict(np.asarray(observation,dtype=np.float32),deterministic=self.deterministic,
                                       action_masks=channel_mask(mask,self.channels))
        for channel,value in zip(self.channels,np.atleast_1d(predicted),strict=True):
            action[channel]=int(value)
        return action


@dataclass(frozen=True)
class CompositePolicy:
    """Rule actions overridden channel by channel with frozen networks."""
    rule:RulePolicy
    frozen:tuple=()

    def action(self,observation,mask,rules=None):
        action=self.rule.action(observation,mask,rules)
        for part in self.frozen:part.apply(observation,mask,action)
        return action


class IrrigationOnly(gym.Wrapper):
    """Discrete(6) action; nitrogen and spray exactly share the rule baseline."""
    def __init__(self,env,policy,*,rules=None):
        super().__init__(env);self.rule_policy=policy;self.rules=rules or ResourceRules()
        self.action_space=gym.spaces.Discrete(len(self.rules.water_grid));self.last_observation=None
    def reset(self,**kwargs):
        observation,info=self.env.reset(**kwargs);self.last_observation=observation.copy();return observation,info
    def action_masks(self):
        return self.env.get_wrapper_attr('action_masks')()[:6].copy()
    def step(self,action):
        if self.last_observation is None:raise ValueError('Reset first')
        if not self.action_space.contains(action):raise ValueError('Invalid irrigation action')
        mask=self.env.get_wrapper_attr('action_masks')()
        if not mask[int(action)]:raise ValueError('Masked irrigation action')
        combined=self.rule_policy.action(self.last_observation,mask,self.rules);combined[0]=int(action)
        observation,reward,terminated,truncated,info=self.env.step(combined)
        self.last_observation=None if terminated or truncated else observation.copy()
        return observation,reward,terminated,truncated,info
