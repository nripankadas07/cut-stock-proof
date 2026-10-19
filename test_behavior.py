import itertools
import unittest
from cut_stock_proof import plan

def data(lengths, stock=10, kerf=0):
 return dict(stock_length=stock,kerf=kerf,pieces=[dict(id=str(i),length=x) for i,x in enumerate(lengths)])

def brute(items, capacity):
 best=len(items)
 def visit(i,free):
  nonlocal best
  if i==len(items):best=min(best,len(free));return
  for j in range(len(free)):
   if free[j]>=items[i]:
    free[j]-=items[i];visit(i+1,free);free[j]+=items[i]
  if len(free)<best:visit(i+1,free+[capacity-items[i]])
 visit(0,[]);return best

class Behavior(unittest.TestCase):
 def test_greedy_counterexample(self):
  r=plan(data([6,5,3,2,2,2]));self.assertEqual((r['first_fit_bar_count'],r['bar_count']),(3,2))
 def test_exhaustive_small_oracle(self):
  for n in range(1,6):
   for lengths in itertools.combinations_with_replacement(range(1,6),n):
    for kerf in (0,1):
     r=plan(data(lengths,6,kerf));self.assertEqual(r['bar_count'],brute([x+kerf for x in lengths],6+kerf),(lengths,kerf))
     ids=[p['id'] for b in r['bars'] for p in b['pieces']];self.assertEqual(sorted(ids),sorted(str(i) for i in range(n)))
     self.assertTrue(all(b['piece_length']+b['kerf_loss']+b['unused']==6 and b['unused']>=0 for b in r['bars']))
 def test_between_piece_kerf(self):
  self.assertEqual(plan(data([5,5],10,1))['bar_count'],2)
  self.assertEqual(plan(data([10],10,99))['bars'][0]['kerf_loss'],0)
 def test_quantity_identity(self):
  d=data([2]);d['pieces'][0]['quantity']=3;r=plan(d)
  self.assertEqual([p['copy'] for p in r['bars'][0]['pieces']],[1,2,3])
 def test_infeasible(self):self.assertEqual(plan(data([11]))['status'],'infeasible')
 def test_budget(self):
  with self.assertRaisesRegex(ValueError,'budget'):plan(data([6,5,3,2,2,2]),1)
 def test_bool_and_duplicate_ids(self):
  for d in (data([True]),dict(stock_length=10,kerf=0,pieces=[dict(id='a',length=1),dict(id='a',length=2)])):
   with self.assertRaises(ValueError):plan(d)
 def test_caps_and_fields(self):
  for d in (data([1]*25),dict(data([1]),other=0),data([0])):
   with self.assertRaises(ValueError):plan(d)
