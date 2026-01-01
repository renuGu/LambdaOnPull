# Performance examples (N^2, inefficient string concat, repeated DB calls)

def slow_concat(lines):
    s=""
    for line in lines:
        s += line
    return s

def fast_concat(lines):
    return "".join(lines)

def slow_nested(items):
    res=[]
    for a in items:
        for b in items:
            if a['id']==b['id']:
                res.append((a,b))
    return res

def fast_nested(items):
    lookup={i['id']:i for i in items}
    return [(i,lookup[i['id']]) for i in items]
