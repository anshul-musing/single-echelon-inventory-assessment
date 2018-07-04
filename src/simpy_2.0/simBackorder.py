
"""This module simulates a single-echelon supply chain
and calculates inventory profile (along with associated inventory 
parameters such as on-hand, inventory position, service level, etc.) 
across time

The system follows a reorder point-reorder quantity policy
If inventory position <= ROP, an order of a fixed reorder 
quantity (ROQ) is placed by the facility

It is assumed that any unfulfilled order is backordered
and is fulfilled whenever the material is available in the
inventory.  The service level is estimated based on how
late the order was fulfilled

Demand is assumed to be Normally distributed
Lead time is assumed to follow a uniform distribution
"""

__author__ = 'Anshul Agarwal'


from SimPy.Simulation import *
import numpy as np

# Stocking facility class
class stockingFacility(Process):

    # initialize the new facility object
    def __init__(self, initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime):
        Process.__init__(self)
        self.on_hand_inventory = initialInv
        self.inventory_position = initialInv
        self.ROP = ROP
        self.ROQ = ROQ
        self.meanDemand = meanDemand
        self.demandStdDev = demandStdDev
        self.minLeadTime = minLeadTime
        self.maxLeadTime = maxLeadTime
        self.totalDemand = 0.0
        self.totalBackOrder = 0.0
        self.totalLateSales = 0.0
        self.serviceLevel = 0.0

    # main subroutine for facility operation
    # it records all stocking metrics for the facility
    def runOperation(self):
        while True:
            yield hold, self, 1.0
            demand = float(np.random.normal(self.meanDemand, self.demandStdDev, 1))
            self.totalDemand += demand
            shipment = min(demand + self.totalBackOrder, self.on_hand_inventory)
            self.on_hand_inventory -= shipment
            self.inventory_position -= shipment
            backorder = demand - shipment
            self.totalBackOrder += backorder
            self.totalLateSales += max(0.0, backorder)
            if self.inventory_position <= 1.01 * self.ROP:  # multiply by 1.01 to avoid rounding issues
                order = newOrder(self.ROQ)
                activate(order, order.ship(self))
                self.inventory_position += self.ROQ


"""Class for a new order placed by the facility
Whenever facility places an order, a new object of
the following class is created
"""
class newOrder(Process):

    def __init__(self, orderQty):
        Process.__init__(self)
        self.orderQty = orderQty

    def ship(self, stock):
        leadTime = int(np.random.uniform(stock.minLeadTime, stock.maxLeadTime, 1))
        yield hold, self, leadTime  # wait for the lead time before delivering
        stock.on_hand_inventory += self.orderQty


# Simulation module
def simulateNetwork(seedinit, initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime):
    initialize()  # initialize SimPy simulation instance
    np.random.seed(seedinit)
    s = stockingFacility(initialInv, ROP, ROQ, meanDemand, demandStdDev, minLeadTime, maxLeadTime)
    activate(s, s.runOperation())
    simulate(until=365)  # simulate for 1 year
    s.serviceLevel = 1 - s.totalLateSales / s.totalDemand
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
