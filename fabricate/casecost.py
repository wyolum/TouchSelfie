from pylab import *
from numpy import *



'''
Qty 1,000:	$7.03 ea	
Qty 3,500:	$6.60 ea	
Qty 5,000:	$6.17 ea	
Qty 20,000:	$6.11 ea
'''
tooling = 14000
n = arange(10000)
pc = (7.03 * (n < 1000) +
      6.60 * (logical_and(1000<= n, n < 3500)) +
      6.17 * (logical_and(3500<= n, n < 5000)) +
      6.11 * (logical_and(5000<= n, n < 20000))
)

cost = (tooling + n * pc) / n
print cost
target = 15.

onoff = 6
power_supply = 14
power_cord = 3.8
display = 60 ## element 14
raspi = 35
sd = 5
parts = {'onoff':onoff,
         'power_supply': power_supply,
         'power_cord':power_cord,
         'display':display,
         'raspi':raspi,
         'sd':sd,
         'camera':25}
total = 0
pts = []
keys = []
for i, key in enumerate(parts):
    keys.append(key)
    text(6000, 120 - i * 120/15., '$%.0f' % parts[key], ha='right')
    text(6200, 120 - i * 120/15., key, ha='left')
    total += parts[key]
    
text(6500, 120 - (len(parts) + 0) * 120/15., '-' * 40,
     ha='center')
text(6000, 120 - (len(parts) + 1) * 120/15., '$%.0f' % total, ha='right')
text(6200, 120 - (len(parts) + 1) * 120/15., 'total', ha='left')

plot(n, cost)
plot(n, cost + total)
plot(n, 78. * ones(len(n)) + total)
ylabel("Cost per part")
yticks(arange(0, 201, 20), ['$%.2f' % p for p in arange(0, 201, 20)])
match = where(cost < target)[0][0]
plot(match, target, 'ro')
plot([match, match], [0, target], 'r--')
plot([0, match], [target, target], 'r--')
for i in range(1000, 5001, 1000):
    text(1700, 50 - i/150, '%4d ==> $%.2f' % (i, cost[i]))
    text(2000, 150 - i/150, '%4d ==> $%.2f' % (i, cost[i] + total))
xlabel("Number produced")
title("PiCase Injection Molding")
legend(["Case Only", "Complete"])
ylim(0, 300)
xlim(0, 300)
show()
