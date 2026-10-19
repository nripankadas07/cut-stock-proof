"""Bounded exact one-dimensional cutting-stock search; no machine control."""
import argparse
import json
import sys


def plan(data, budget=250000):
    if not isinstance(data, dict) or set(data) != {'stock_length', 'kerf', 'pieces'}:
        raise ValueError('expected stock_length, kerf, pieces only')
    def integer(v, lo, hi):
        if type(v) is not int or not lo <= v <= hi:
            raise ValueError('integer outside supported bounds')
        return v
    stock = integer(data['stock_length'], 1, 1000000)
    kerf = integer(data['kerf'], 0, 1000000)
    integer(budget, 1, 250000)
    if not isinstance(data['pieces'], list) or not 1 <= len(data['pieces']) <= 24:
        raise ValueError('expected 1..24 piece types')
    pieces, seen = [], set()
    for p in data['pieces']:
        if not isinstance(p, dict) or set(p) - {'id', 'length', 'quantity'} or not {'id','length'} <= set(p):
            raise ValueError('invalid piece fields')
        name = p['id']
        if not isinstance(name, str) or not name or len(name) > 64 or not name.isascii() or any(ord(c)<32 for c in name) or name in seen:
            raise ValueError('piece IDs must be unique printable ASCII')
        seen.add(name)
        length = integer(p['length'], 1, 1000000)
        quantity = integer(p.get('quantity', 1), 1, 24)
        pieces.extend((name, i + 1, length) for i in range(quantity))
        if len(pieces) > 24:
            raise ValueError('at most 24 expanded pieces')
    if any(p[2] > stock for p in pieces):
        return {'status': 'infeasible', 'reason': 'a piece exceeds stock length'}
    pieces.sort(key=lambda p: (-p[2], p[0], p[1]))
    weights = [p[2] + kerf for p in pieces]
    capacity = stock + kerf
    lower = (sum(weights) + capacity - 1) // capacity
    greedy, remaining = [], []
    for i, weight in enumerate(weights):
        target = next((j for j, r in enumerate(remaining) if r >= weight), len(remaining))
        if target == len(remaining):
            remaining.append(capacity); greedy.append([])
        remaining[target] -= weight; greedy[target].append(i)
    best = [b[:] for b in greedy]
    nodes = 0
    def search(index, bins, free):
        nonlocal nodes, best
        nodes += 1
        if nodes > budget:
            raise ValueError('search budget exceeded; optimality not established')
        if len(best) == lower:
            return
        if index == len(pieces):
            if len(bins) < len(best): best = [b[:] for b in bins]
            return
        if len(bins) >= len(best): return
        w = weights[index]
        tried = set()
        for j, r in enumerate(free):
            if r >= w and r not in tried:
                tried.add(r); free[j] -= w; bins[j].append(index)
                search(index + 1, bins, free)
                bins[j].pop(); free[j] += w
                if len(best) == lower: return
        if len(bins) + 1 < len(best):
            bins.append([index]); free.append(capacity - w)
            search(index + 1, bins, free)
            free.pop(); bins.pop()
    search(0, [], [])
    bars = []
    for indices in best:
        material = sum(pieces[i][2] for i in indices)
        loss = kerf * (len(indices) - 1)
        bars.append({'pieces': [{'id':pieces[i][0], 'copy':pieces[i][1], 'length':pieces[i][2]} for i in indices],
                     'piece_length':material, 'kerf_loss':loss, 'unused':stock-material-loss})
    return {'status':'optimal', 'stock_length':stock, 'kerf_between_pieces':kerf,
            'bar_count':len(best), 'lower_bound':lower, 'first_fit_bar_count':len(greedy),
            'proof':'lower_bound_met' if len(best)==lower else 'exhaustive_search',
            'search_nodes':nodes, 'bars':bars}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input'); parser.add_argument('--budget', type=int, default=250000)
    args = parser.parse_args()
    try:
        with open(args.input, 'rb') as f: raw=f.read(65537)
        if len(raw)>65536: raise ValueError('input exceeds 64 KiB')
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d: raise ValueError('duplicate JSON key')
                d[k]=v
            return d
        result=plan(json.loads(raw, object_pairs_hook=unique), args.budget)
        print(json.dumps(result, indent=2)); return 0 if result['status']=='optimal' else 1
    except (OSError, ValueError, UnicodeError, RecursionError) as e:
        print(str(e),file=sys.stderr); return 2


if __name__ == '__main__': sys.exit(main())
