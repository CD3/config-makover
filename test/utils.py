
class Approx(object):
  def __init__(self,val):
    self.val = val
    self.epsilon = 0.01
  def epsilon(self,epsilon):
    self.epsilon = epsilon
  def __eq__(self,other):
    return abs(other - self.val) <= self.epsilon*abs(other + self.val)/2
