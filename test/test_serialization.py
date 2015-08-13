import lxml.etree, dpath,  dicttoxml, xmltodict
import ruamel.yaml

d = { 'var1' : 1
    , 'list1' : [ 2, 3, 4 ]
    , 'nest1' : { 'var1' : 11 }
    }


text = dicttoxml.dicttoxml( d )
# print text
data = xmltodict.parse( text )

def get_path( e ):
  path = [e.tag]
  while not e.getparent() is None:
    e = e.getparent()
    path.insert(0, e.tag)
  return path


tree = lxml.etree.fromstring( text )
# print lxml.etree.tostring(tree)


text = '''
var1 : 1
list1 :
  - 11
  - 12
nest1 :
    var1 : 11
    var2 : !!float 12
    var3 : '{{var1 + 2}}'
    '@var3_type' : float
'''

d = ruamel.yaml.load( text )
print d
