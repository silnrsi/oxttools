#!/usr/bin/python

import lxml.etree as et
import re, copy, sys
from lxml.etree import XPathEvalError

tmpl = "{uri://nrsi.sil.org/template/0.1}"
tmpla = "{uri://nrsi.sil.org/template_attributes/0.1}"

assert sys.version_info.major >= 3, "Requires Python 3"

class IterDict(object) :
    def __init__(self) :
        self.keys = {}
        self.values = []
        self.indices = []
        self.atstart = True

    def __setitem__(self, key, value) :
        if isinstance(value, str) or not hasattr(value, 'len') :
            value = [value]
        self.keys[key] = len(self.values)
        self.values.append(value)
        self.indices.append(0)

    def asdict(self) :
        res = {}
        for k, i in self.keys.items() :
            res[k] = str(self.values[i][self.indices[i]])
        return res

    def __iter__(self) :
        return self

    def __next__(self) :
        if self.atstart :
            self.atstart = False
            return self.asdict()
        for i in range(len(self.indices)) :
            if self.indices[i] + 1 < len(self.values[i]) : 
                self.indices[i] += 1
                return self.asdict()
        raise StopIteration

def asstr(v) :
    if isinstance(v, str) : return v
    elif isinstance(v, et._Element) : return v.text
    elif len(v) == 0 : return ''
    v = v[0]
    if isinstance(v, et._Element) :
        return v.text
    return v

docs = {}
class Templater(object) :

    def __init__(self, mergefile=None) :
        self.vars = {}
        self.ns = {}
        self.fns = copy.copy(self.extensions)
        if mergefile is not None:
            self.mergedoc = et.parse(mergefile)
            self.ns = self.mergedoc.getroot().nsmap
        else:
            self.mergedoc = None

    def define(self, name, val) :
        self.vars[name] = val

    def addfn(self, ns, name, fn) :
        self.fns[(ns, name)] = fn

    def addns(self, nsmap):
        self.ns.update(nsmap)

    def parse(self, fname) :
        self.doc = et.parse(fname)
        self.ns.update(self.doc.getroot().nsmap)

    def __str__(self) :
        return et.tounicode(self.doc)

    def process(self, root = None, context = None, nest = False) :
        if nest :
            oldvars = self.vars.copy()
        if root is None :
            root = self.doc.getroot()
        if context is None :
            context = root
        for c in list(root) :
            if str(c.tag).startswith(tmpl) :
                name = c.tag[len(tmpl):]
                if name == 'variable' :
                    self.processattrib(c, context)
                    k = c.attrib[tmpl+'name']
                    if not tmpl+"fallback" in c.attrib or not k in self.vars :
                        v = self.xpath(c.text, context, c)
                        if isinstance(v, (str, list)) and len(v) == 0 :
                            v = c.attrib.get(tmpl+'default', '')
                        self.vars[k] = v
                elif name == 'namespace':
                    self.processattrib(c, context)
                    k = c.attrib[tmpl+'name']
                    self.ns[k] = c.text
                elif name == 'value' :
                    self.processattrib(c, context)
                    v = self.xpath(c.attrib[tmpl+"path"], context, c)
                    t = asstr(v)
                    root.text = t if tmpl+"cdata" not in c.attrib or t == '' else et.CDATA(t)
                elif name == 'if' :
                    self.processattrib(c, context)
                    v = self.xpath(c.attrib[tmpl+"path"], context, c)
                    if v :
                        index = root.index(c)
                        node = self.process(root = c, context = context, nest=True)
                        if node is None : node = []
                        for n in list(node) :
                            node.remove(n)
                            root.insert(index, n)
                            index += 1
                elif name == 'context' :
                    self.processattrib(c, context)
                    index = root.index(c)
                    node = self.process(root = c, context = self.xpath(c.attrib[tmpl+"path"], context, c), nest=True)
                    if node is None : node = []
                    for n in list(node) :
                        node.remove(n)
                        root.insert(index, n)
                        index += 1
                elif name == 'foreach' :
                    uppervars = self.vars.copy()
                    index = root.index(c)
                    itervars = IterDict()
                    nodes = []
                    for k, v in c.attrib.items() :
                        if k.startswith(tmpla) :
                            newk = k[len(tmpla):]
                            newv = self.xpath(v, context, c)
                            itervars[newk] = newv
                    for v in itervars :
                        self.vars = uppervars.copy()
                        self.vars.update(v)
                        if tmpl + "path" in c.attrib:
                            pathnodes = self.xpath(c.attrib[tmpl+"path"], context, c)
                            if not isinstance(pathnodes, list) :
                                pathnodes = [pathnodes]
                        else :
                            pathnodes = [context]
                        for n in pathnodes :
                            x = copy.deepcopy(c)
                            nodes.append(self.process(root = x, context = n, nest = True))
                    for n in nodes :
                        if n is None : continue
                        for r in n :
                            n.remove(r)
                            root.insert(index, r)
                            index += 1
                elif name == "includepath":
                    if self.mergedoc is not None:
                        index = root.index(c)
                        nodes = self.xpathall(c.attrib[tmpl+"path"], self.mergedoc, c)
                        for n in nodes:
                            root.insert(index, n)
                            index += 1
                root.remove(c)
            elif len(c) :
                self.processattrib(c, context)
                self.process(c, context=context, nest=False)
            else :
                self.processattrib(c, context)
        if nest :
            self.vars = oldvars
        return root

    def processattrib(self, node, context) :
        for k, v in node.attrib.items() :
            if k.startswith(tmpla) :
                newk = k[len(tmpla):]
                for t in node.attrib.keys() :
                    if t.endswith(newk) and (len(t) == len(newk) or (t[-len(newk)-1] == '}' and t[:-len(newk)] != tmpla)) :
                        newk = t[:-len(newk)] + newk
                        break
                newv = asstr(self.xpath(v, context, node))
                if newv != '' :
                    node.set(newk, newv)
                del node.attrib[k]

    def _uritag(self, tag):
        bits = tag.split(':')
        if len(bits) == 2 and bits[0] in self.doc.getroot().nsmap:
            return "{" + self.doc.getroot().nsmap[bits[0]] + "}" + bits[1]
        else:
            return tag

    def _scanendfor(self, root, start, var, mode, match):
        for i, c in enumerate(root[start:]):
            if c.tag == self._uritag('text:hidden-text'):
                v = c.attrib[self._uritag('text:string-value')]
                if ' ' in v:
                    (command, rest) = v.split(' ', 1)
                else:
                    (command, rest) = (v, '')
                if command == match:
                    if rest == var:
                        res = self._upscanmode(mode, c, err="Unexpected endfor mode")
                        return (res, i)
            else:
                res, resi= self._scanendfor(c, 0, var, mode, match)
                if res is not None:
                    return (res, i)
        return (None, 0)

    def _upscan(self, start, errorctxt, *tags):
        testtags = [self._uritag(x) for x in tags]
        top = self._uritag('office:text')
        res = start.getparent()
        while res.tag not in testtags:
            if res.tag == top:
                raise SyntaxError("cannot find {} above {}".format(tags[0], errorctxt))
            res = res.getparent()
        return res

    def _upscanmode(self, mode, c, err="Unknown for type"):
        if mode == 'para':
            return self._upscan(c, 'for para', 'text:p', 'text:h')
        elif mode == 'row':
            return self._upscan(c, 'for row', 'table:table-row')
        elif mode == "text":
            return c
        else:
            raise SyntaxError(err)

    def processodt(self, root=None, parent=None, index=0, context=None, infor=None):
        if root is None :
            root = self.doc.getroot().find('.//' + self._uritag('office:text'))
            parent = root.getparent()
            self.ns = context.nsmap
        i = 0
        while i < len(root):
            c = root[i]
            if c.tag == self._uritag('text:hidden-text'):
                v = c.attrib[self._uritag('text:string-value')]
                if ' ' in v:
                    (command, rest) = v.split(' ', 1)
                else:
                    (command, rest) = (v, '')
                if command in ('value', 'fvalue'):
                    value = self.xpath(rest, context, c)
                    if command == "fvalue" and not asstr(value) and "fallback" in self.vars:
                        value, isfallback = self.xpath_aliases(rest, context, self.vars['fallback'])
                        if asstr(value) and isfallback:
                            c.set(self._uritag("text:style-name"), "Fallback")
                    c.tag = self._uritag('text:span')
                    res = asstr(value)
                    lines = res.strip().split("\n") if res is not None else [""]
                    c.text = lines.pop(0)
                    for l in lines:
                        s = et.SubElement(c, self._uritag("text:line-break"))
                        s.tail = l.strip()
                elif command == 'variable':
                    var, rest = rest.split(' ', 1)
                    value = self.xpath(rest, context, c)
                    self.vars[var] = value
                elif command == "condvar":
                    var, test, rest = rest.split(' ', 2)
                    value = asstr(self.xpath(test, context, c))
                    for r in rest.split(' '):
                        k, v = r.split("=")
                        if value == k or k == "":
                            self.vars[var] = v
                            break
                    else:
                        self.vars[var] = ""
                elif command in ('forenum', 'forstr', 'for'):
                    (mode, var, rest) = rest.split(' ', 2)
                    if var == infor:
                        i += 1
                        continue
                    start = self._upscanmode(mode, c)
                    forparent = start.getparent()
                    if forparent is None:
                        forparent = start
                        if c in start:
                            starti = start.index(c)
                        else:
                            starti = 0
                    else:
                        starti = forparent.index(start)
                    (end, endi) = self._scanendfor(forparent, starti, var, mode, "endfor")
                    if end is not None:
                        endparent = end.getparent()
                        if endparent is None:
                            endparent = end
                        else:
                            endi = endparent.index(end)
                    if end is None or forparent != endparent:
                        raise SyntaxError(f"Unbalanced for for {var}")
                    replacements = []
                    if command == 'for' or command == 'forstr':
                        vals = self.xpathall(rest, context, c)
                    elif command == 'forenum':
                        vals = rest.split(' ')
                    tempbase = forparent[starti:endi+1]
                    tempend = len(forparent) - endi
                    for j, val in enumerate(vals):
                        ctx = val if command == 'for' else context
                        memo = {}
                        temp = [x.__deepcopy__(memo) for x in tempbase]
                        if start == forparent:
                            newp = start.makeelement(start.tag, nsmap=self.ns)
                            newp.extend(temp)
                            temp = [newp]
                        forparent[endi+1+j*len(temp):endi+1+j*len(temp)] = temp
                        oldvars = self.vars.copy()
                        self.vars[var] = val
                        self.processodt(root=temp, context=ctx, infor=var)
                        self.vars = oldvars
                        replacements.extend(temp)
                    forparent[starti:endi+1] = []
                    return (forparent, len(forparent) - tempend + 1)
                elif command == 'endfor':
                    pass
                elif command == "ifin":
                    (mode, ident, val, rest) = rest.split(' ', 3)
                    start = self._upscanmode(mode, c)
                    ifparent = start.getparent()
                    end, endi = self._scanendfor(ifparent, ifparent.index(start), ident, mode, "endif")
                    if end is None or start.getparent() != end.getparent():
                        raise SyntaxError("Unbalanced if")
                    starti = ifparent.index(start)
                    endi = ifparent.index(end)
                    value = self.xpath(val, context, c)
                    vstr = asstr(value)
                    if not len(vstr) or vstr not in rest:
                        ifparent[starti:endi + 1] = []
                        return (ifparent, starti)
                elif command == "ifval":
                    (mode, ident, var, rest) = rest.split(' ', 3)
                    start = self._upscanmode(mode, c) 
                    ifparent = start.getparent()
                    if mode == "text" and ifparent.tag == self._uritag("text:span"):
                        start = ifparent
                        ifparent = ifparent.getparent()
                    end, endi = self._scanendfor(ifparent, ifparent.index(start), ident, mode, "endif")
                    if end is None or start.getparent() != end.getparent():
                        if mode == "text" and end is not None:
                            end = end.getparent()
                        if end is None or start.getparent() != end.getparent():
                            raise SyntaxError("Unbalanced if")
                    starti = ifparent.index(start)
                    endi = ifparent.index(end)
                    value = self.xpath(rest, context, c)
                    vstr = asstr(value)
                    self.vars[var] = vstr
                    if not len(vstr):
                        ifparent[starti:endi+1] = []
                        return (ifparent, starti)
                elif command == "endif":
                    pass
                i += 1
            else:
                newroot, i = self.processodt(root=c, parent=root, index=i, context=context, infor=infor)
                if newroot is not root:
                    return (newroot, i)
        return (parent, index+1)

    def xpathall(self, path, context, base):
        try:
            res = context.xpath(path, extensions=self.fns, smart_strings=False, namespaces=self.ns, **self.vars)
        except XPathEvalError as e:
            raise SyntaxError("{} in xpath expression: {}".format(e.args[0], path))
        return res

    def xpath(self, path, context, base) :
        res = self.xpathall(path, context, base)
        if not isinstance(res, str) and len(res) == 1 :
            res = res[0]
        return res

    def xpathtext(self, path, context, base):
        res = self.xpathall(path, context, base)
        if res is None:
            return ""
        if isinstance(res, str):
            return res
        else:
            return res[0].text

    def _getaliascontext(self, context, path, a, kw):
        try:
            context = context.xpath(path, **kw)
        except XPathEvalError:
            context = None
        if context is not None and len(context):
            try:
                context = context[0].xpath(a)
            except XPathEvalError:
                context = None
        if context is not None and not len(context):
            context = None
        return context if context is None else context[0]

    def xpath_aliases(self, path, context, fbcontext):
        ''' returns result and whether it came from the fbcontext '''
        origpath = path
        kw = dict(extensions=self.fns, smart_strings=False, namespaces=self.ns)
        kw.update(self.vars)
        if context is not None:
            try:
                res = context.xpath(path, **kw)
            except XPathEvalError:
                pass
            else:
                if len(res):
                    return (res[0], False)
        exts = []
        while len(path):
            try:
                res = fbcontext.xpath(path, **kw)
            except XPathEvalError as e:
                res = []
            if not len(res):
                if "/" not in path:
                    res = [fbcontext]
                    exts = [path]
                    path = ""
                else:
                    path, ext = path.rsplit("/", 1)
                    exts.append(ext)
                    continue
            if not len(exts):
                return (res[0], True)
            if isinstance(res[0], str) or len(res[0]) != 1 or getattr(res[0][0], 'tag', '') != 'alias':
                return ([], True)
                raise ValueError(f"Alias not found at {path} in {res} for {path}/{'/'.join(exts)}")
            a = res[0][0].get('path')
            while a.startswith("../"):
                if not len(path):
                    path = ".."
                elif path.startswith(".."):
                    path = a[:3] + path
                else:
                    path, _ = path.rsplit("/", 1)
                a = a[3:]
            if len(path):
                path += "/" + a
            else:
                path = a
            path += "/" + "/".join(exts)
            return self.xpath_aliases(path, context, fbcontext)

# xpath functions
    @staticmethod
    def fn_doc(context, txt) :
        txt = asstr(txt)
        if txt not in docs :
            docs[txt] = et.parse(txt)
        return docs[txt].getroot()

    @staticmethod
    def fn_firstword(context, txt) :
        txt = asstr(txt)
        if txt == '' : return txt
        return txt.split()[0]

    @staticmethod
    def fn_findsep(context, val, index) :
        val = asstr(val)
        if val == '' : return val
        return val.split()[int(index)]

    @staticmethod
    def fn_replace(context, txt, regexp, repl) :
        txt = asstr(txt)
        repl = asstr(repl)
        try :
            res = re.sub(regexp, repl, txt)
        except Exception as e :
            raise et.XPathEvalError(e.message + ": txt = {}, regexp = {}, repl = {}".format(txt, regexp, repl))
        return res

    @staticmethod
    def fn_dateformat(context, txt, *formats) :
        """Converts LDML date/time format letters to LibreOffice corresponding codes"""
        txt = asstr(txt)
        return txt

    @staticmethod
    def fn_choose(context, test, a, b) :
        return a if test else b

    @staticmethod
    def fn_split(control, *vals) :
        res = []
        for x in vals:
            if isinstance(x, (list, tuple)):
                for v in x:
                    res.extend(asstr(v).split())
            else:
                res.extend(asstr(x).split())
        return res

    @staticmethod
    def fn_default(control, *vals) :
        for v in vals :
            x = asstr(v)
            if x != '' :
                return x
        return ''

    @staticmethod
    def fn_concat(context, a, b):
        return a + b

    @staticmethod
    def fn_set(context, *vals):
        s = set()
        for v in vals:
            if isinstance(v, (list, tuple)):
                s.update(v)
            else:
                s.add(v)
        return sorted(s)

    @staticmethod
    def fn_ucfirst(context, s):
        return s.title()
        
    extensions = {
        (None, 'doc') : fn_doc.__func__,
        (None, 'firstword') : fn_firstword.__func__,
        (None, 'findsep') : fn_findsep.__func__,
        (None, 'replace') : fn_replace.__func__,
        (None, 'dateformat') : fn_dateformat.__func__,
        (None, 'choose') : fn_choose.__func__,
        (None, 'split') : fn_split.__func__,
        (None, 'default') : fn_default.__func__,
        (None, 'concat') : fn_concat.__func__,
        (None, 'set') : fn_set.__func__,
        (None, 'ucfirst') : fn_ucfirst.__func__,
    }


if __name__ == '__main__' :
    import sys, os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('infile',help='xml file to process')
    parser.add_argument('outfile',help='Ouptut file to generate')
    parser.add_argument('-t','--template',help='Template file to generate from')
    parser.add_argument('-l','--langtag',help='Maximal Langtag for this data')
    args = parser.parse_args()
    if args.template is None:
        args.template = 'simple_report.fodt'
    t = Templater()
    t.define('resdir', os.path.abspath(os.path.join(os.path.dirname(__file__), "data")))

    if args.langtag is not None:
        try:
            from sldr.langtags import LangTag
        except ImportError:
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../../sldr/sldr/python/lib'))
            from sldr.langtags import LangTag
        ltag = LangTag(args.langtag)
        t.define('lang', ltag.lang)
        t.define('script', ltag.script)
        t.define('lscript', ltag.script.lower())
        t.define('region', ltag.region)

    t.parse(args.template)
    oldd = et.parse(args.infile).getroot()
    nsmap = oldd.nsmap
    nsmap['sil'] = 'urn://www.sil.org/ldml/0.1'
    d = et.Element(oldd.tag, nsmap=nsmap)
    d[:] = oldd[:]
    if args.template.endswith('.fodt'):
        t.processodt(context=d)
    else:
        t.process(context = d)
    with open(args.outfile, "w", encoding="utf-8") as of :
        of.write("<?xml version='1.0'?>\n")
        of.write(unicode(t))

