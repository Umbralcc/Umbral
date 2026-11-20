import json,sys
d=json.load(open(sys.argv[1])); W=sorted((a,b,w) for v in d.values() for s in v for a,b,w in s['words'])
for r in sys.argv[2:]:
    a0,b0=map(float,r.split('-')); print('##',r)
    print(' '.join(f"{w.strip()}[{a:.1f}-{b:.1f}]" for a,b,w in W if a0<=a<=b0))
