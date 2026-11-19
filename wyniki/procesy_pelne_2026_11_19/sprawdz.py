from pathlib import Path
import xml.etree.ElementTree as E
import json
P=Path(__file__).resolve().parent
N={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL','d':'http://www.omg.org/spec/BPMN/20100524/DI'}
results=[]
for f in sorted(P.glob('*.bpmn')):
 r=E.parse(f).getroot();allids=[x.get('id') for x in r.iter() if x.get('id')];ids=set(allids);idx={x.get('id'):x for x in r.iter() if x.get('id')};errors=[]
 if len(allids)!=len(ids):errors.append('Powtórzone identyfikatory')
 for x in r.iter():
  for k in ('sourceRef','targetRef','bpmnElement','processRef','attachedToRef','messageRef','errorRef'):
   if x.get(k) and x.get(k) not in ids:errors.append(f'{x.get("id")}: brak {k}={x.get(k)}')
  typ=x.tag.split('}')[-1]
  if typ in ('incoming','outgoing') and x.text not in ids:errors.append('Brak przepływu '+str(x.text))
 for owner in list(r.findall('b:process',N))+list(r.findall('.//b:subProcess',N)):
  children={x.get('id') for x in owner if x.get('id')}
  for flow in owner.findall('b:sequenceFlow',N):
   a=flow.get('sourceRef');b=flow.get('targetRef');fid=flow.get('id')
   if a not in children or b not in children:errors.append('Przekroczona granica procesu: '+fid);continue
   if fid not in [x.text for x in idx[a].findall('b:outgoing',N)]:errors.append('Brak outgoing '+fid)
   if fid not in [x.text for x in idx[b].findall('b:incoming',N)]:errors.append('Brak incoming '+fid)
  if 'uzupelniony' in f.name:
   flows=owner.findall('b:sequenceFlow',N);targets={x.get('targetRef') for x in flows};starts={x.get('id') for x in owner if x.tag.split('}')[-1]=='startEvent'}
   starts|={x.get('id') for x in owner if x.tag.split('}')[-1] in ('userTask','serviceTask') and x.get('id') not in targets}
   reachable=set(starts)
   for _ in range(len(children)):
    for fl in flows:
     if fl.get('sourceRef') in reachable:reachable.add(fl.get('targetRef'))
   for x in owner:
    if x.tag.split('}')[-1] in ('startEvent','endEvent','userTask','serviceTask','sendTask','exclusiveGateway') and x.get('id') not in reachable:errors.append('Nieosiągalny '+x.get('id'))
 results.append({'file':f.name,'ids':len(ids),'diagrams':len(r.findall('d:BPMNDiagram',N)),'errors':errors})
# Regression checks for the corrected code order.
for name in ['xml_szczegoly.bpmn','manual_szczegoly.bpmn']:
 r=E.parse(P/name).getroot();flow=list(r.findall('.//b:sequenceFlow',N));assert any(x.get('sourceRef','').endswith('_Archive') and x.get('targetRef','').endswith('_Created') for x in flow)
assert all(not x['errors'] for x in results),results
(P/'KONTROLA.json').write_text(json.dumps({'structural_validation':results,'runtime_test':False,'visual_paradigm_import_test':False},ensure_ascii=False,indent=2)+'\n')
print('OK:',len(results),'BPMN;',sum(x['diagrams'] for x in results),'płaszczyzny; referencje, granice procesów, incoming/outgoing i osiągalność widoków głównych.')
