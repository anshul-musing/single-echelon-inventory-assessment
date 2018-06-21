# single-echelon inventory simulation with SimPy

The modules in this repo simulates a single-echelon supply chain
and calculates inventory profile (along with associated inventory 
parameters such as on-hand, inventory position, service level, etc.) 
across time.  We use SimPy discrete event simulation package.

The system follows a reorder point-reorder quantity (ROP-ROQ) policy.  
If inventory position <= ROP, an order of a fixed quantity (ROQ)
is placed by the facility

Demand is assumed to be Normally distributed.  
Lead time is assumed to follow a uniform distribution

The two modules differ in the following way:

* simBackorder.py:

    It is assumed that any unfulfilled order is backordered
    and is fulfilled whenever the material is available in the 
    inventory.  The service level is estimated based on how 
    late the order was fulfilled

* simLostSales.py

    It is assumed that any unfulfilled order is lost.  The 
    service level is estimated based on how much of the 
    demand was fulfilled

The modules have been used to validate literature models.  The
validation study is published [here]

[here]: https://arxiv.org/abs/1806.07427
