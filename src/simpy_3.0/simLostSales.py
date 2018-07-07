
"""This module simulates a single-echelon supply chain
and calculates inventory profile (along with associated inventory 
parameters such as on-hand, inventory position, service level, etc.) 
across time

The system follows a reorder point-reorder quantity policy
If inventory position <= ROP, an order of a fixed reorder 
quantity (ROQ) is placed by the facility

It is assumed that any unfulfilled order is lost
The service level is estimated based on how much
of the demand was fulfilled

Demand is assumed to be Normally distributed
Lead time is assumed to follow a uniform distribution
"""

__author__ = 'Anshul Agarwal'


import simpy
import numpy as np

# Stocking facility class
class stockingFacility(object):

    # initialize the new facility object
    def __init__(self, env, initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime):
        self.env = env
        self.on_hand_inventory = initialInv
        self.inventory_position = initialInv
        self.ROP = ROP
        self.ROQ = ROQ
        self.meanDemand = meanDemand
        self.demandStdDev = demandStdDev
        self.minLeadTime = minLeadTime
        self.maxLeadTime = maxLeadTime
        self.totalDemand = 0.0
        self.totalShipped = 0.0
        self.serviceLevel = 0.0
        env.process(self.runOperation())

    # main subroutine for facility operation
    # it records all stocking metrics for the facility
    def runOperation(self):
        while True:
            yield self.env.timeout(1.0)
            demand = float(np.random.normal(self.meanDemand, self.demandStdDev, 1))
            self.totalDemand += demand
            shipment = min(demand, self.on_hand_inventory)
            self.totalShipped += shipment
            self.on_hand_inventory -= shipment
            self.inventory_position -= shipment
            if self.inventory_position <= 1.01 * self.ROP:  # multiply by 1.01 to avoid rounding issues
                self.env.process(self.ship(self.ROQ))
                self.inventory_position += self.ROQ

    # subroutine for a new order placed by the facility
    def ship(self, orderQty):
        leadTime = int(np.random.uniform(self.minLeadTime, self.maxLeadTime, 1))
        yield self.env.timeout(leadTime)  # wait for the lead time before delivering
        self.on_hand_inventory += orderQty


# Simulation module
def simulateNetwork(seedinit, initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime):
    env = simpy.Environment()  # initialize SimPy simulation instance
    np.random.seed(seedinit)
    s = stockingFacility(env, initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime)
    env.run(until=365)  # simulate for 1 year
    s.serviceLevel = s.totalShipped / s.totalDemand
    return s


######## Main statements to call simulation ########
meanDemand = 500.0
demandStdDev = 100.0
minLeadTime = 7
maxLeadTime = 13
CS = 5000.0
ROQ = 6000.0
ROP = max(CS,ROQ)
initialInv = ROP + ROQ

# Simulate
replications = 100
sL = []
for i in range(replications):
    nodes = simulateNetwork(i,initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime)
    sL.append(nodes.serviceLevel)

sLevel = np.array(sL)
print "Avg. service level: " + str(np.mean(sLevel))
print "Service level standard deviation: " + str(np.std(sLevel))
