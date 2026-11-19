"""Lokalne modele AS-IS: widoki porównywalne + szczegóły BPMN, bez sieci."""
from pathlib import Path
import xml.etree.ElementTree as E
import copy, json, subprocess, textwrap, hashlib, html
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
B='http://www.omg.org/spec/BPMN/20100524/MODEL'; D='http://www.omg.org/spec/BPMN/20100524/DI'; C='http://www.omg.org/spec/DD/20100524/DC'; I='http://www.omg.org/spec/DD/20100524/DI'
for k,v in [('bpmn',B),('bpmndi',D),('dc',C),('di',I)]:E.register_namespace(k,v)
NS={'b':B,'d':D,'c':C,'i':I}
def q(tag):return '{'+B+'}'+tag
def el(parent,tag,**attrs):return E.SubElement(parent,q(tag),{k:str(v) for k,v in attrs.items()})
def local(x):return x.tag.split('}')[-1]
def doc(x,t):el(x,'documentation').text=t

def layout(root,owner,plane,ox=70,oy=70):
    """Graphviz computes positions; persisted as standard BPMN DI."""
    nodes=[x for x in owner if local(x) in ('startEvent','endEvent','serviceTask','sendTask','userTask','task','subProcess','callActivity','exclusiveGateway','parallelGateway','intermediateCatchEvent','intermediateThrowEvent')]
    flows=[x for x in owner if local(x)=='sequenceFlow']; ids={x.get('id') for x in nodes}
    dot=['digraph G { rankdir=LR; graph [nodesep=0.8,ranksep=0.9]; node [shape=box,width=2.6,height=1.0,fixedsize=true];']
    for x in nodes:
        typ=local(x); wh='width=0.65,height=0.65' if 'Event' in typ else 'width=0.9,height=0.9' if 'Gateway' in typ else 'width=2.6,height=1.0'
        dot.append(json.dumps(x.get('id'))+' ['+wh+'];')
    for x in flows:dot.append(json.dumps(x.get('sourceRef'))+' -> '+json.dumps(x.get('targetRef'))+';')
    dot.append('}')
    out=subprocess.run(['dot','-Tplain'],input='\n'.join(dot),text=True,capture_output=True,check=True).stdout
    import shlex
    lines=[shlex.split(x) for x in out.splitlines()]; gh=float(lines[0][3])*72; coords={}
    for a in lines:
        if a[0]=='node':
            _,id,x,y,w,h,*_=a; w=float(w)*72;h=float(h)*72
            coords[id]=(ox+float(x)*72-w/2,oy+gh-float(y)*72-h/2,w,h)
    for x in nodes:
        id=x.get('id'); xx,yy,w,h=coords[id]
        sh=E.SubElement(plane,'{'+D+'}BPMNShape',id=id+'_auto_di',bpmnElement=id)
        if local(x)=='subProcess':sh.set('isExpanded','false')
        E.SubElement(sh,'{'+C+'}Bounds',x=str(xx),y=str(yy),width=str(w),height=str(h))
    for f in flows:
        s=coords[f.get('sourceRef')];t=coords[f.get('targetRef')]
        points=[(s[0]+s[2],s[1]+s[3]/2),(t[0],t[1]+t[3]/2)]
        if abs(points[0][1]-points[1][1])>2:
            mx=(points[0][0]+points[1][0])/2;points=[points[0],(mx,points[0][1]),(mx,points[1][1]),points[1]]
        edge=E.SubElement(plane,'{'+D+'}BPMNEdge',id=f.get('id')+'_auto_di',bpmnElement=f.get('id'))
        for x,y in points:E.SubElement(edge,'{'+I+'}waypoint',x=str(x),y=str(y))
    return coords

def rewire(owner,edges):
    for n in list(owner):
        if local(n)=='sequenceFlow':owner.remove(n)
        else:
            for ch in list(n):
                if local(ch) in ('incoming','outgoing'):n.remove(ch)
    index={n.get('id'):n for n in owner}
    for i,(s,t,name) in enumerate(edges,1):
        id=owner.get('id')+'_F'+str(i);f=el(owner,'sequenceFlow',id=id,sourceRef=s,targetRef=t)
        if name:f.set('name',name);el(f,'conditionExpression').text=name
        el(index[s],'outgoing').text=id;el(index[t],'incoming').text=id

def corrected_full(kind):
    source=ROOT/({'ckan':'harvester_ckan_L2_szczegolowy.bpmn','xml':'harvester_xml_L2_szczegolowy.bpmn','manual':'reczne_dodawanie_zasobu/reczne_dodawanie_zasobu.bpmn'}[kind])
    root=E.parse(source).getroot(); root.set('exporter','Lokalna analiza AS-IS 2026-11-19');root.set('exporterVersion','2.0')
    doc(root,'Uzupełnienie 19.11.2026: model AS-IS lokalnego mcod 2.62.3. Pierwsza ocena nie czeka na konwersje. Import i publikacja działają asynchronicznie. Brak projektowanych blokad PDF/0/1 i brak nowej flagi archiwum. Pozostałe szczegóły odziedziczone z wcześniejszych modeli; nie jest to test produkcji.')
    if kind=='xml':
        sub=root.find('.//b:subProcess[@id="XML_L2_Conversions_Convert"]',NS)
        pre='XML_L2_Conversions_Convert_ConvertDetail_';g=lambda x:pre+x
        # Actual code: increase_openness_score -> dataset.archive_files -> if derived: score/refresh.
        edges=[(g('Start'),g('CSV'),''),(g('CSV'),g('MakeCSV'),'tak'),(g('CSV'),g('Merge'),'nie'),(g('MakeCSV'),g('Merge'),''),(g('Merge'),g('JSONLD'),''),(g('JSONLD'),g('MakeJSONLD'),'tak'),(g('JSONLD'),g('Archive'),'nie'),(g('MakeJSONLD'),g('Archive'),''),(g('Archive'),g('Created'),''),(g('Created'),g('Refresh'),'tak'),(g('Created'),g('End'),'nie'),(g('Refresh'),g('End'),'')]
        rewire(sub,edges)
        sub.find('b:exclusiveGateway[@id="'+g('CSV')+'"]',NS).set('name','XLS/XLSX zasobu lub wnętrza; nie linked; są dane i tabela?')
        sub.find('b:sendTask[@id="'+g('Archive')+'"]',NS).set('name','Zleć paczkę plików zbioru z opóźnieniem')
        doc(sub,'Bezpośrednio sprawdzono resources/tasks/process_resource_file_data.py:45 oraz Resource.increase_openness_score. Wyjątek przed zleceniem archiwum przerywa dalszy przebieg; nie ma gwarancji utworzenia pochodnej.')
        for d in root.findall('d:BPMNDiagram',NS):
            pl=d.find('d:BPMNPlane',NS)
            if pl.get('bpmnElement')==sub.get('id'):
                for child in list(pl):pl.remove(child)
                layout(root,sub,pl)
    if kind=='manual':
        # Expand manual conversions using the same verified implementation as XML.
        xml=corrected_full('xml'); template=xml.find('b:process[@id="XML_L2_Conversions"]',NS)
        old=root.find('b:process[@id="RECZNE_Konwersje"]',NS)
        new=copy.deepcopy(template)
        mapping={x.get('id'):x.get('id').replace('XML_L2_Conversions','RECZNE_Konwersje') for x in new.iter() if x.get('id')}
        mapping['XML_L2_Conversions_Start']='RECZNE_Konwersje_start';mapping['XML_L2_Conversions_End']='RECZNE_Konwersje_end';mapping['XML_L2_Conversions_Convert']='RECZNE_Konwersje_convert'
        for x in new.iter():
            for k,v in list(x.attrib.items()):
                if v in mapping:x.set(k,mapping[v])
                elif k=='messageRef':del x.attrib[k]
            if x.text in mapping:x.text=mapping[x.text]
        new.set('name','Pliki pochodne, paczka zbioru i ponowna ocena')
        root.remove(old);root.insert(3,new)
        # Remove obsolete conversion DI and reconstruct visible collapsed process in pool.
        valid={x.get('id') for x in root.iter() if x.get('id')}
        for d in list(root.findall('d:BPMNDiagram',NS)):
            pl=d.find('d:BPMNPlane',NS)
            if pl.get('bpmnElement') not in valid:root.remove(d);continue
            for x in list(pl):
                if x.get('bpmnElement') not in valid:pl.remove(x)
        overview=root.find('d:BPMNDiagram/d:BPMNPlane',NS)
        for x in list(overview):
            if x.get('bpmnElement','').startswith('RECZNE_Konwersje_') and x.get('bpmnElement')!='RECZNE_Konwersje_Pool':overview.remove(x)
        pool=overview.find('d:BPMNShape[@bpmnElement="RECZNE_Konwersje_Pool"]/c:Bounds',NS)
        oy=float(pool.get('y'))+90 if pool is not None else 1700
        layout(root,new,overview,100,oy)
        for xd in xml.findall('d:BPMNDiagram',NS):
            xpl=xd.find('d:BPMNPlane',NS)
            if xpl.get('bpmnElement')=='XML_L2_Conversions_Convert':
                d=copy.deepcopy(xd)
                for x in d.iter():
                    for k,v in list(x.attrib.items()):
                        if v in mapping:x.set(k,mapping[v])
                        elif v.startswith('XML_L2_Conversions'):x.set(k,v.replace('XML_L2_Conversions','RECZNE_Konwersje'))
                root.append(d)
        for x in root.iter():
            if local(x)=='documentation' and x.text and 'tylko is_published' in x.text:x.text=x.text.replace('tylko is_published','tylko opublikowany, nieusunięty i nietrwale usunięty')
    return root

class Overview:
    def __init__(self,key,title):
        self.key=key;self.root=E.Element(q('definitions'),id='VIEW_'+key,targetNamespace='urn:mcod:as-is:2026-11-19',exporter='Lokalna analiza kodu',exporterVersion='2.0'); self.coll=el(self.root,'collaboration',id='VIEW_'+key+'_coll',name=title)
        d=E.SubElement(self.root,'{'+D+'}BPMNDiagram',id='VIEW_'+key+'_diagram',name=title);self.pl=E.SubElement(d,'{'+D+'}BPMNPlane',id='VIEW_'+key+'_plane',bpmnElement=self.coll.get('id'));self.nodes={};self.count=0
        doc(self.root,'AS-IS mcod 2.62.3. Pule oznaczają niezależne przebiegi; linie przerywane to zlecenia bez oczekiwania. Widok rozwinięty uzupełnia szczegółowy plik *_szczegoly.bpmn. Nie obejmuje projektowanych blokad i nowej flagi is_archive.')
    def pool(self,id,name):
        y=70+self.count*300;self.count+=1;pr=el(self.root,'process',id=self.key+'_'+id,isExecutable='false',name=name);pa=el(self.coll,'participant',id=pr.get('id')+'_pool',name=name,processRef=pr.get('id'))
        sh=E.SubElement(self.pl,'{'+D+'}BPMNShape',id=pa.get('id')+'_di',bpmnElement=pa.get('id'),isHorizontal='true');E.SubElement(sh,'{'+C+'}Bounds',x='40',y=str(y),width='3800',height='280');return pr,y
    def node(self,pr,y,id,name,col,kind='serviceTask',lower=False,documentation=''):
        id=self.key+'_'+id;w,h=(44,44) if 'Event' in kind else (58,58) if 'Gateway' in kind else (190,76)
        x=110+col*240;yy=y+(170 if lower else 65);n=el(pr,kind,id=id,name=name)
        if documentation:doc(n,documentation)
        sh=E.SubElement(self.pl,'{'+D+'}BPMNShape',id=id+'_di',bpmnElement=id);E.SubElement(sh,'{'+C+'}Bounds',x=str(x),y=str(yy),width=str(w),height=str(h));self.nodes[id]=(pr,n,(x,yy,w,h));return id
    def flow(self,a,b,label='',message=False):
        pr,an,s=self.nodes[a];_,bn,t=self.nodes[b];id=self.key+'_flow_'+str(len(list(self.root.iter())))
        f=el(self.coll if message else pr,'messageFlow' if message else 'sequenceFlow',id=id,sourceRef=a,targetRef=b)
        if label:f.set('name',label)
        if not message:el(an,'outgoing').text=id;el(bn,'incoming').text=id
        p1=(s[0]+s[2],s[1]+s[3]/2);p2=(t[0],t[1]+t[3]/2)
        if message:
            p1=(s[0]+s[2]/2,s[1]+s[3]);p2=(t[0]+t[2]/2,t[1]);corridor=3890+(len(self.coll.findall(q('messageFlow')))%12)*18;sy=70+int((s[1]-70)//300)*300+290;ty=70+int((t[1]-70)//300)*300+42;pts=[p1,(p1[0],sy),(corridor,sy),(corridor,ty),(p2[0],ty),p2]
        elif abs(p2[0]-p1[0])>280 and abs(p1[1]-p2[1])<50:
            route=70+int((s[1]-70)//300)*300+150+(len(pr.findall(q('sequenceFlow')))%3)*6;p1=(s[0]+s[2]/2,s[1]+s[3]);p2=(t[0]+t[2]/2,t[1]+t[3]);pts=[p1,(p1[0],route),(p2[0],route),p2]
        elif abs(p1[1]-p2[1])>1:
            if p2[0]<p1[0]:mid=max(s[1]+s[3],t[1]+t[3])+22;pts=[p1,(p1[0]+15,p1[1]),(p1[0]+15,mid),(p2[0]-15,mid),(p2[0]-15,p2[1]),p2]
            else:mx=(p1[0]+p2[0])/2;pts=[p1,(mx,p1[1]),(mx,p2[1]),p2]
        else:pts=[p1,p2]
        edge=E.SubElement(self.pl,'{'+D+'}BPMNEdge',id=id+'_di',bpmnElement=id)
        for x,y in pts:E.SubElement(edge,'{'+I+'}waypoint',x=str(x),y=str(y))
    def chain(self,ids):
        for a,b in zip(ids,ids[1:]):self.flow(a,b)


def overview(kind):
    o=Overview(kind,{'ckan':'1. CKAN — import, ocena i publikacja','xml':'2. XML — import, pliki, ocena i konwersje','manual':'3. Ręczne dodanie — plik lub URL, ocena i konwersje'}[kind]);N=o.node
    if kind!='manual':
        p,y=o.pool('setup','ADMINISTRATOR I HARMONOGRAM — aktywacja lub należny termin')
        a=N(p,y,'config','Skonfiguruj i zapisz źródło '+kind.upper(),0);b=N(p,y,'activation','Nowe aktywne źródło / aktywacja?',1,'exclusiveGateway');c=N(p,y,'sendimport','Zleć import po zatwierdzeniu zapisu',2,'sendTask');end=N(p,y,'setupend','Koniec konfiguracji',3,'endEvent');o.chain([a,b]);o.flow(b,c,'Tak');o.flow(b,end,'Nie');o.flow(c,end)
        timer=N(p,y,'timer','Termin przeglądu źródeł',4,'startEvent');check=N(p,y,'due','Sprawdź aktywność i termin importu',5);g=N(p,y,'duetest','Import należny?',6,'exclusiveGateway');send=N(p,y,'timersend','Zleć import',7,'sendTask');te=N(p,y,'timerend','Koniec cyklu',8,'endEvent');o.chain([timer,check,g]);o.flow(g,send,'Tak');o.flow(g,te,'Nie');o.flow(send,te)
        p,y=o.pool('import','HARWESTER I KATALOG — import metadanych; koniec importu nie czeka na ocenę')
        start=N(p,y,'importstart','Odebrano zlecenie importu',0,'startEvent');active=N(p,y,'active','Źródło nadal aktywne?',1,'exclusiveGateway');fetch=N(p,y,'fetch','Pobierz API i odczytaj JSON' if kind=='ckan' else 'Pobierz XML; sprawdź HTTP, MD5 i XSD',2);val=N(p,y,'validate','Zweryfikuj cały wykaz i opisy zasobów',3);ok=N(p,y,'valid','Wymagane kontrole poprawne?',4,'exclusiveGateway');rules=N(p,y,'rules','Oceń zbiory osobno: licencja i reguły HVD/DGA' if kind=='ckan' else 'Odczytaj dane, dokumenty, statusy i reguły HVD/DGA',5);save=N(p,y,'save','Zapisz przyjęte zbiory i każdy zasób; obsłuż sygnały',6);sync=N(p,y,'sync','Wycofaj pozycje nieobecne na przyjętej liście',7);res=N(p,y,'result','Zapisz wynik, liczniki i koniec importu',8);iend=N(p,y,'importend','Koniec importu metadanych',9,'endEvent');err=N(p,y,'inputerr','Zapisz błąd importu; nie zastępuj katalogu błędnym wykazem',4,lower=True);ee=N(p,y,'inputerrend','Koniec z błędem / pominięcie',5,'endEvent',True)
        o.chain([start,active]);o.flow(active,fetch,'Tak');o.flow(active,ee,'Nie');o.chain([fetch,val,ok]);o.flow(ok,rules,'Tak');o.flow(ok,err,'Nie');o.flow(err,ee);o.chain([rules,save,sync,res,iend]);o.flow(c,start,message=True);o.flow(send,start,message=True)
        doc(o.nodes[res][1],'CKAN: OK / OK_PARTIAL zależnie od odrzuconych zbiorów. XML: błąd wymaganej walidacji wykazu zatrzymuje przyjęcie; szczegóły i błędy zapisu w *_szczegoly.bpmn.')
    else:
        p,y=o.pool('form','PANEL ADMINISTRACYJNY — formularz i zapis')
        fs=N(p,y,'formstart','Dodawanie zasobu',0,'startEvent');a=N(p,y,'form_input','Wskaż plik z dysku lub URL; uzupełnij opis i status',1,'userTask');v=N(p,y,'formvalidation','Sprawdź formularz i szczególne wymagania',2);g=N(p,y,'formok','Formularz poprawny?',3,'exclusiveGateway');fix=N(p,y,'fix','Pokaż błędy; popraw formularz',3,'userTask',True);save=N(p,y,'save','Zapisz zasób; dla uploadu zapisz plik główny',4);fe=N(p,y,'formend','Zapis zakończony; praca w tle może trwać',5,'endEvent');o.flow(save,fe);o.chain([fs,a,v,g]);o.flow(g,fix,'Nie');o.flow(fix,a);o.flow(g,save,'Tak');res=None
    p,y=o.pool('dispatch','ZAPIS ZASOBU — decyzja o przygotowaniu; zlecenie po zatwierdzeniu transakcji')
    dstart=N(p,y,'dispatchstart','Obsługa zapisu / sygnału zasobu',0,'startEvent');cond=N(p,y,'condition','Stan i zmiana wymagają przygotowania?',1,'exclusiveGateway');dsend=N(p,y,'prepsend','Zleć przygotowanie URL' if kind=='manual' else 'Zleć właściwe zadanie przygotowania',3 if kind=='manual' else 2,'sendTask');de=N(p,y,'dispatchend','Koniec obsługi zapisu',5 if kind=='manual' else 3,'endEvent');o.chain([dstart,cond]);o.flow(cond,de,'Nie — m.in. nowy szkic');o.flow(dsend,de);o.flow(save,dstart,message=True)
    if kind=='manual':
        choice=N(p,y,'inputchoice','Nowy plik główny czy zewnętrzny URL?',2,'exclusiveGateway');dsendupload=N(p,y,'uploadsend','Zleć kontrolę zapisanego pliku głównego',3,'sendTask',True);o.flow(cond,choice,'Tak');o.flow(choice,dsend,'URL');o.flow(choice,dsendupload,'Plik');o.flow(dsendupload,de)
    else:o.flow(cond,dsend,'Tak')
    doc(o.nodes[cond][1],'Zapis nie oznacza zawsze nowej oceny. Nowy opublikowany zasób / zmiana linku lub dostępności / właściwa zmiana wymuszonego typu / przywrócenie; nowy główny plik opublikowanego zasobu ma osobny sygnał. Sam opis lub format nie gwarantuje oceny. Zmiana znaków umownych ma odrębną ścieżkę. Szczegółowe warunki w modelu szczegółowym.')
    conversions=[];refreshes=[]
    def prep(upload=False):
        suffix='upload' if upload else 'url';p,y=o.pool('prep_'+suffix,'PRZYGOTOWANIE W TLE — '+('plik z dysku' if upload else ('CKAN: link i zapisany format' if kind=='ckan' else 'URL zasobu XML' if kind=='xml' else 'URL zasobu')))
        ids=[]
        def add(id,name,col,typ='serviceTask',low=False):return N(p,y,suffix+'_'+id,name,col,typ,low)
        st=add('start','Odebrano zlecenie',0,'startEvent')
        if kind=='ckan':
            url=add('url','Pomiń pobranie lokalnej kopii CKAN; etap kończy się sukcesem',1);skip=add('skip','Standardowo brak pliku głównego: bez lokalnej kontroli i tabeli',2);score=add('score','Oblicz i zapisz stopień z formatu i treści linku',3);date=add('date','Zapisz datę weryfikacji, jeżeli żądana',4);ok=add('ok','Przygotowanie udane, bez odroczonych wyjątków?',5,'exclusiveGateway');pub=add('pub','Nadal opublikowany i nieusunięty?',6,'exclusiveGateway');rf=add('refresh','Zleć odświeżenie ES/RDF',7,'sendTask');end=add('end','Koniec zadania',8,'endEvent');problem=add('problem','Obsłuż błąd; brak końcowego odświeżenia',6,'serviceTask',True);o.chain([st,url,skip,score,date,ok]);o.flow(ok,pub,'Tak');o.flow(ok,problem,'Nie');o.flow(pub,rf,'Tak');o.flow(pub,end,'Nie');o.flow(rf,end);o.flow(problem,end);refreshes.append(rf)
            doc(o.nodes[skip][1],'Standardowe nowe zasoby CKAN nie dostają kopii. Wspólny entrypoint ma warunki kontroli istniejącego pliku; nietypowe wcześniej istniejące pliki wymagają analizy aktualnego stanu. Nie jest to globalny zakaz konwersji w całym systemie.')
        else:
            src=add('src','Wczytaj zapisany plik główny' if upload else 'Sprawdź URL i rozpoznaj typ; dla pliku zapisz kopię główną',1);need=add('need','Można i trzeba kontrolować plik?',2,'exclusiveGateway') if not upload else None;file=add('file','Sprawdź plik: format, MIME, kodowanie i archiwum',3);fg=add('fileok','Kontrola pliku udana?',4,'exclusiveGateway');eligible=add('eligible','Dane kwalifikują się do tabeli?',5,'exclusiveGateway');data=add('data','Ustal schemat, sprawdź i zindeksuj dane',6);indexed=add('indexed','Wynik indeksacji success dodatni?',7,'exclusiveGateway');derive=add('derive','Zleć pliki pochodne po zatwierdzeniu indeksacji',8,'sendTask');score=add('score','Oblicz i zapisz stopień: pliki albo link',9);date=add('date','Zapisz datę weryfikacji, jeżeli żądana',10);ok=add('ok','Wymagane etapy udane, bez odroczonych wyjątków?',11,'exclusiveGateway');pub=add('pub','Nadal opublikowany i nieusunięty?',12,'exclusiveGateway');rf=add('refresh','Zleć odświeżenie ES/RDF',13,'sendTask');end=add('end','Koniec zadania',14,'endEvent');problem=add('problem','Zaloguj / zgłoś problem; bez końcowego odświeżenia',12,'serviceTask',True)
            o.chain([st,src]);
            if need:o.flow(src,need);o.flow(need,file,'Tak');o.flow(need,score,'Nie / brak pliku')
            else:o.flow(src,file)
            o.chain([file,fg]);o.flow(fg,eligible,'Tak');o.flow(fg,score,'Nie — ocena dostępnego stanu');o.flow(eligible,data,'Tak');o.flow(eligible,score,'Nie');o.chain([data,indexed]);o.flow(indexed,derive,'Tak');o.flow(indexed,score,'Nie');o.flow(derive,score);o.chain([score,date,ok]);o.flow(ok,pub,'Tak');o.flow(ok,problem,'Nie');o.flow(pub,rf,'Tak');o.flow(pub,end,'Nie');o.flow(rf,end);o.flow(problem,end);conversions.append(derive);refreshes.append(rf)
            doc(o.nodes[eligible][1],'Plik główny; format zasobu lub wnętrza CSV/TSV/XLS/XLSX/ODS/SHP; instytucja inna niż developer. Bez kwalifikacji pomija się dane tabeli, nie samą ocenę. success może współistnieć z failed; nie oznacza poprawności każdego wiersza.')
        if upload:doc(o.nodes[src][1],'Entrypoint pliku najpierw ładuje ResourceFile i nieusunięty Resource; brak rekordu może przerwać zadanie. Po kontroli danych, przy update_link, udanej kontroli pliku i braku odroczonych błędów zapisuje wynik linku SUCCESS bez pobierania HTTP, a potem oblicza ocenę. Szczegóły w entrypoint_res_file.py.')
        doc(o.nodes[score][1],'Brak wartości formatu całego zasobu: 0. Brak pliku głównego i istniejący link: ocena linku. W przeciwnym razie maksimum ocen pliku głównego i pochodnych. Błąd obliczenia może przerwać zadanie przed nowym zapisem. Reguły archiwów i formatów są rozwinięte w szczegółach. Ocena nie stanowi blokady publikacji w obecnym kodzie.')
        o.flow(dsendupload if upload else dsend,st,('Upload' if upload else 'URL') if kind=='manual' else '',True)
    prep()
    if kind=='manual':prep(True)
    if kind!='ckan':
        p,y=o.pool('conversion','PLIKI POCHODNE W TLE — wspólny algorytm XML i ręcznego dodania')
        st=N(p,y,'convstart','Odebrano zlecenie konwersji',0,'startEvent');g=N(p,y,'xls','XLS/XLSX, nie linked, są dane i tabela?',1,'exclusiveGateway');csv=N(p,y,'csv','Utwórz lub odtwórz pochodny CSV UTF-8',2);jg=N(p,y,'csvavailable','Dostępny CSV do konwersji, poza archiwum?',3,'exclusiveGateway');jl=N(p,y,'jsonld','Spróbuj utworzyć / odtworzyć JSON-LD',4);arch=N(p,y,'archsend','Zleć paczkę plików zbioru z opóźnieniem',5,'sendTask');created=N(p,y,'created','Powstał / odtworzono plik pochodny?',6,'exclusiveGateway');sc=N(p,y,'rescore','Ponownie oblicz i zapisz ocenę wszystkich plików',7);pg=N(p,y,'convpub','Nadal opublikowany i nieusunięty?',8,'exclusiveGateway');rf=N(p,y,'convrefresh','Zleć odświeżenie ES/RDF z nową oceną',9,'sendTask');ce=N(p,y,'convend','Koniec konwersji',10,'endEvent');o.chain([st,g]);o.flow(g,csv,'Tak');o.flow(g,jg,'Nie');o.flow(csv,jg);o.flow(jg,jl,'Tak');o.flow(jg,arch,'Nie');o.flow(jl,arch);o.chain([arch,created]);o.flow(created,sc,'Tak');o.flow(created,ce,'Nie — bez ponownej oceny');o.chain([sc,pg]);o.flow(pg,rf,'Tak');o.flow(pg,ce,'Nie');o.flow(rf,ce);refreshes.append(rf)
        for sender in conversions:o.flow(sender,st,message=True)
        doc(o.nodes[g][1],'XML: linked to availability=remote; ręczne: linked to zewnętrzny URL. Konwersja do CSV uwzględnia format zasobu lub wnętrza archiwum. Brak linked nie jest warunkiem próby JSON-LD z dostępnego CSV. Pierwsza ocena nie czeka na to zadanie.')
        doc(o.nodes[arch][1],'Kod zleca dataset.archive_files po powrocie increase_openness_score, przed warunkowym przeliczeniem oceny; także gdy nie powstał plik. Nieprzechwycony wyjątek wcześniej przerywa tę ścieżkę. Paczka plików to nie projektowana flaga archiwum.')
        p,y=o.pool('archive','PACZKA PLIKÓW ZBIORU — niezależne zadanie')
        ar=N(p,y,'archstart','Odebrano zlecenie po opóźnieniu',0,'startEvent');disk=N(p,y,'disk','Wystarczające wolne miejsce?',1,'exclusiveGateway');build=N(p,y,'build','Przygotuj ZIP plików zbioru i zaktualizuj odnośnik',2);ae=N(p,y,'archend','Koniec zadania paczki',3,'endEvent');no=N(p,y,'nospace','Zaloguj brak miejsca; pomiń budowę',1,lower=True);o.chain([ar,disk]);o.flow(disk,build,'Tak');o.flow(disk,no,'Nie');o.flow(no,ae);o.flow(build,ae);o.flow(arch,ar,message=True)
    p,y=o.pool('publication','PUBLIKACJA W TLE — osobne zadania zależne od zdarzenia zapisu / oceny')
    ps=N(p,y,'pubstart','Odebrano odpowiednie zlecenie',0,'startEvent');pt=N(p,y,'pubtasks','Wykonaj zlecone aktualizacje ES/API, RDF i powiadomień',1);pe=N(p,y,'pubend','Koniec danego zadania publikacji',2,'endEvent');o.chain([ps,pt,pe])
    doc(o.nodes[pt][1],'To agregacja niezależnych zadań, a nie ich kolejność. Zapis/zmiana stanu może zlecić publikację przed ukończeniem przygotowania. Końcowe odświeżenie po ocenie zleca ES/RDF, nie automatycznie każdy rodzaj powiadomienia. Szczegóły mapy sygnałów i odbiorców w modelach szczegółowych.')
    o.flow(save,ps,'Według zdarzenia zapisu',True)
    for r in refreshes:o.flow(r,ps,'ES/RDF',True)
    return o.root

# SVG renderer: local and dependency-free; clickable activities open their documentation.
def svg(root,diagram):
    idx={x.get('id'):x for x in root.iter() if x.get('id')};pl=diagram.find('d:BPMNPlane',NS);shapes=pl.findall('d:BPMNShape',NS);edges=pl.findall('d:BPMNEdge',NS)
    bounds=[]
    for sh in shapes:
        b=sh.find('c:Bounds',NS)
        if b is not None:bounds.append(tuple(float(b.get(k)) for k in ('x','y','width','height')))
    if not bounds:return ''
    x0=min(x for x,y,w,h in bounds)-40;y0=min(y for x,y,w,h in bounds)-65;w=max(x+w for x,y,w,h in bounds)-x0+80;h=max(y+h for x,y,w,h in bounds)-y0+100
    edgepoints=[(float(p.get('x')),float(p.get('y'))) for ed in edges for p in ed.findall('i:waypoint',NS)]
    if edgepoints:w=max(w,max(x for x,y in edgepoints)-x0+60);h=max(h,max(y for x,y in edgepoints)-y0+60)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" role="img" aria-label="{html.escape(diagram.get("name", "Diagram"),quote=True)}"><defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0 L10 4 L0 8Z" fill="#344c67"/></marker></defs><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="white"/><style>text{{font-family:Arial,sans-serif;fill:#20334b;font-size:13px}}.node{{cursor:pointer}}.node:hover rect{{stroke:#147e75;stroke-width:3}}</style>']
    # Pools first, edges second, tasks last.
    for sh in shapes:
        elx=idx.get(sh.get('bpmnElement'));b=sh.find('c:Bounds',NS)
        if elx is None or b is None or local(elx) not in ('participant','lane'):continue
        x,y,ww,hh=[float(b.get(k)) for k in ('x','y','width','height')]
        out.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="#f5f8fc" stroke="#bac8d8"/><text x="{x+15}" y="{y+24}" font-weight="bold">{html.escape(elx.get("name", ""))}</text>')
    for edge in edges:
        f=idx.get(edge.get('bpmnElement'))
        if f is None:continue
        pts=[(float(p.get('x')),float(p.get('y'))) for p in edge.findall('i:waypoint',NS)]
        if not pts:continue
        dashed=local(f)!='sequenceFlow';attr='stroke-dasharray="7 5"' if dashed else ''
        out.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="#344c67" stroke-width="1.6" {attr} marker-end="url(#arrow)"/>')
        if f.get('name'):
            x,y=pts[1] if len(pts)>2 else ((pts[0][0]+pts[-1][0])/2,(pts[0][1]+pts[-1][1])/2);out.append(f'<text x="{x+5}" y="{y-8}" paint-order="stroke" stroke="white" stroke-width="4">{html.escape(f.get("name"))}</text>')
    for sh in shapes:
        n=idx.get(sh.get('bpmnElement'));b=sh.find('c:Bounds',NS)
        if n is None or b is None or local(n) in ('participant','lane'):continue
        x,y,ww,hh=[float(b.get(k)) for k in ('x','y','width','height')];typ=local(n);name=n.get('name') or n.findtext('b:text','',NS);desc=n.findtext('b:documentation','',NS);out.append('<g class="node"><title>'+html.escape(name+'\n'+desc)+'</title>')
        if 'Event' in typ:
            out.append(f'<circle cx="{x+ww/2}" cy="{y+hh/2}" r="{min(ww,hh)/2}" fill="'+('#f5d9df' if typ=='endEvent' else '#e3f2ed')+'" stroke="#344c67" stroke-width="'+('3' if typ=='endEvent' else '1.6')+'"/>');tx=x+ww/2;ty=y+hh+17;lines=textwrap.wrap(name,28)
        elif 'Gateway' in typ:
            out.append(f'<polygon points="{x+ww/2},{y} {x+ww},{y+hh/2} {x+ww/2},{y+hh} {x},{y+hh/2}" fill="#fff0d4" stroke="#b58030"/><text x="{x+ww/2}" y="{y+hh/2+5}" text-anchor="middle">'+('+' if typ=='parallelGateway' else '×')+'</text>');tx=x+ww/2;ty=y-12-13*(len(textwrap.wrap(name,30))-1);lines=textwrap.wrap(name,30)
        elif typ=='textAnnotation':tx=x+ww/2;ty=y+16;lines=textwrap.wrap(name,max(16,int(ww/7)))
        else:
            fill='#fff0d4' if any(t in name.lower() for t in ['stopień','ocenę','oceny','otwartości']) else '#fff'
            out.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" rx="8" fill="{fill}" stroke="#46637f"/>');lines=textwrap.wrap(name,max(16,int(ww/7)));tx=x+ww/2;ty=y+hh/2-7*(len(lines)-1)+4
            if typ=='subProcess':out.append(f'<text x="{tx}" y="{y+hh-4}" text-anchor="middle" font-weight="bold">⊞</text>')
        out.append(f'<text x="{tx}" y="{ty}" text-anchor="middle">'+''.join(f'<tspan x="{tx}" dy="{0 if i==0 else 15}">{html.escape(line)}</tspan>' for i,line in enumerate(lines))+'</text></g>')
    out.append('</svg>');return ''.join(out)

reports=[]
for key in ['ckan','xml','manual']:
    for typ,root in [('uzupelniony',overview(key)),('szczegoly',corrected_full(key))]:
        fn=key+'_'+typ+'.bpmn';E.indent(root);E.ElementTree(root).write(HERE/fn,encoding='utf-8',xml_declaration=True)
        views=[]
        for i,d in enumerate(root.findall('d:BPMNDiagram',NS)):
            svgtext=svg(root,d);svgn=f'{key}_{typ}_{i+1:02d}.svg';(HERE/svgn).write_text(svgtext);views.append((d.get('name') or d.get('id'),svgn,svgtext))
        reports.append((key,typ,fn,views))

css='''body{margin:0;background:#f2f5f9;color:#20334b;font:16px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:30px}header{background:#16344d;color:white;padding:30px;border-radius:16px}h1{line-height:1.2}h2{margin-top:35px}nav{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}a{color:#175f83}.note{padding:20px;background:#fff1d9;border-left:4px solid #c58b2b;margin:20px 0}.diagram{overflow:auto;background:white;border:1px solid #ccd8e4;border-radius:10px;padding:16px}.diagram svg{display:block;width:3800px;max-width:none;height:auto}.tools{display:flex;gap:8px;align-items:center;margin-bottom:10px}button{padding:6px 12px;cursor:pointer}details{margin:14px 0}summary{cursor:pointer;font-weight:600}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;padding:12px;border:1px solid #d4dfe9;vertical-align:top}code{background:#e5edf4;padding:2px 4px}@media print{nav,.tools{display:none}.diagram svg{width:100%}.diagram{overflow:visible}main{padding:0}header{background:white;color:#20334b}}'''
pages=['<!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CKAN, XML i ręczne dodawanie — kompletne etapy przetwarzania</title><style>'+css+'</style><main><header><p>MCOD 2.62.3 · AS-IS · 19.11.2026</p><h1>Trzy procesy z przygotowaniem, oceną i pracą w tle</h1><p>Widoki porównywalne oraz szczegółowe modele BPMN. Wszystkie pliki działają lokalnie, bez internetu.</p></header>',
'<nav><a href="#ckan">1. CKAN</a><a href="#xml">2. XML</a><a href="#manual">3. Ręczne dodanie</a><a href="KOREKTY_I_ZRODLA.md">Zmiany, źródła i ograniczenia</a></nav>',
'<div class="note"><strong>Korekta wcześniejszych screenów:</strong> XML ma konwersje tak samo jak ręczne dodawanie. CKAN standardowo nie tworzy kopii głównej. Ocena jest zadaniem w tle po zapisie; nie należy traktować kroku zapisu jako synchronicznego nadania oceny. Publiczne opisy mogą być aktualizowane niezależnie od zakończenia przygotowania. Nie dodano projektowanych blokad 0/1 ani flagi archiwum.</div>',
'<table><tr><th>Etap</th><th>CKAN</th><th>XML</th><th>Ręczne dodanie</th></tr><tr><td>Kopia główna</td><td>Standardowo pomijana</td><td>Dla rozpoznanego pliku pobieranego z URL</td><td>Upload lub pobranie z URL</td></tr><tr><td>Dane tabelaryczne i indeksacja</td><td>Standardowo brak lokalnego pliku</td><td>Warunkowo</td><td>Warunkowo</td></tr><tr><td>Konwersje i druga ocena</td><td>Brak standardowej nowej ścieżki konwersji</td><td>Po dodatnim wyniku indeksacji; osobne zadanie</td><td>Te same reguły konwersji</td></tr></table>',
'<p>Przeciągaj pasek przewijania, aby czytać od lewej do prawej. Przyciski zmieniają rozmiar rysunku. Najedź na element, aby przeczytać jego dokumentację. Szczegóły obejmują dodatkowe diagramy, m.in. walidację, zapis, kalkulację formatów, archiwa i błędy.</p>']
for key in ['ckan','xml','manual']:
    pages.append(f'<section id="{key}"><h2>'+{'ckan':'1. Import CKAN','xml':'2. Import XML','manual':'3. Ręczne dodawanie'}[key]+'</h2>')
    for k,typ,fn,views in [x for x in reports if x[0]==key]:
        pages.append(f'<p><a href="{fn}">Pobierz BPMN — '+('widok uzupełniony' if typ=='uzupelniony' else 'szczegóły i podprocesy')+'</a></p>')
        for i,(name,svgn,svgtext) in enumerate(views):
            opened=' open' if typ=='uzupelniony' else ''
            pages.append(f'<details{opened}><summary>{html.escape(name)}'+(' — szczegóły' if typ=='szczegoly' else '')+f'</summary><div class="tools"><button onclick="zoom(this,0.8)">−</button><button onclick="zoom(this,1.25)">+</button><button onclick="fit(this)">Dopasuj szerokość</button><a href="{svgn}">Otwórz SVG</a></div><div class="diagram">{svgtext}</div></details>')
    pages.append('</section>')
pages.append('<footer><p>Źródło: lokalny snapshot mcod 2.62.3. Analiza statyczna, bez uruchomienia aplikacji i bez testu importu w Visual Paradigm. Nowe widoki odwzorowują zakres biznesowy i asynchroniczne granice; szczegóły są w osobnych BPMN i rozwinięciach. To pliki odtworzone na podstawie screenów i źródeł, a nie edycja projektu VPP.</p></footer></main><script>function zoom(b,f){let s=b.parentElement.nextElementSibling.querySelector("svg");s.style.width=((parseFloat(s.style.width)||s.getBoundingClientRect().width)*f)+"px"}function fit(b){let d=b.parentElement.nextElementSibling;d.querySelector("svg").style.width=(d.clientWidth-32)+"px"}</script></html>')
(HERE/'PREZENTACJA.html').write_text('\n'.join(pages))
print('Wygenerowano 6 BPMN oraz',sum(len(x[3]) for x in reports),'widoków SVG i PREZENTACJA.html')
