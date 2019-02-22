import json
import sys

class LogRange():
    def __init__(self):
        self.rows = []

    def appendRow(self, row):
        self.rows.append(row)

    def _mean(self, list, name):
        sum = 0.0;
        for num in list:
            sum += num[name]
        return sum / len(list)

    def _withinPercent(self, val, avg, percent):
        if avg == 0:
            return False
        per = abs(val - avg) / avg * 100
        return per <= percent



    def compute(self):
        map = self._mean(self.rows, 'MAP')
        ve = self._mean(self.rows, 'VEMain')
        rpm = self._mean(self.rows, 'RPM')
        ego = self._mean(self.rows, 'EGO')
        lbd = self._mean(self.rows, 'Lambda')

        for row in self.rows:
            if not self._withinPercent(row['MAP'], map, 3) or \
                not self._withinPercent(row['RPM'], rpm, 5) or \
                not self._withinPercent(row['EGO'], ego, 4):
                    return None
            if row['ETE'] != 100.0:
                return None
        return (map, rpm, ve, ego, lbd, (ego/lbd) * ve)

    def clear(self):
        self.rows = []

    
if __name__ == "__main__":
    log = json.loads(open(sys.argv[1], 'r').read())    
    count = 0
    r = LogRange()
    for row in log:
        r.appendRow(row)
        count += 1
        if count % 10 == 0:
            vals = r.compute()
            if vals is not None:
                if not r._withinPercent(vals[3], vals[4], 3):
                    print "{0},{1},{2},{3},{4},{5}".format(*vals)
            r.clear()
