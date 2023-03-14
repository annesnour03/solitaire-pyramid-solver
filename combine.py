from pprint import pprint
res = []
mine = "KH QH AH JH 2H TH 3H 9H 4H 8H 5H 6H 7H 5S 8S 4S 9S 3S TS 2S JS QS AS 6S 7S KS KD KC".split()
for i in ["A",2,3,4,5,6,7,8,9,"T","J","Q","K"]:
    for j in ["C","H","D","S"]:
        res.append(str(i) + str(j))
diff = (set(res).difference(set(mine)))
for dif in diff:
    print(dif)