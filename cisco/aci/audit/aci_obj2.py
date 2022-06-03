import operator
from operator import itemgetter
from pprint import pprint


def aciobjlist(dict={}, topkey='imdata'):
    data = dict[topkey]
    list = []
    for x in data:
        keys = [*x]
        key = keys[0]
        newObj = aciobj(type=key, dict=x)
        list.append(newObj)
    return list

def filteraciobjlist(list, key):
    new_list = []
    for x in list:
        if x.type == key:
            new_list.append(x)
    return new_list
class aciobj:
    def __init__(self, type='fvTenant', dict={}):
        if dict == {}:
            pprint("New aciobj has no dictionary")
        else:
            self.data = dict[type]
            self.type = type
            self.family = []
            self.attributes = dict[type]['attributes']
            if 'name' in self.attributes.keys():
                self.name = self.attributes['name']
                setattr(self, type, self.name)
            else:
                self.name = ''
            if 'children' in self.data.keys():
                self.children = dict[type]['children']
                self.kids = aciobjlist(dict=self.data, topkey='children')
                self.numkids = len(self.kids)
            else:
                self.children = []
                self.kids = []
                self.numkids = 0

    def setaciattr(self, name, key): ### Creates new attribute from 'attributes'
        try:
            setattr(self, name, self.attributes[key])
        except:
            print(f'Not able to set attribute for {name} and {key}')


    def setaciattrlist(self, key_list):
        if key_list:
            for z in key_list:
                if z in self.attributes:
                    setattr(self, z, self.attributes[z])

    def filterkids(self, name, key, attr_list=[], kid_attr_list=[]):
        # Creates new attribute for specific children in list format
        list = []
        family = []
        if self.numkids != 0:
            for x in self.kids:
                if x.type == key:
                    x.family = [self.type] + self.family
                    setattr(x, 'parent', self.type)
                    for a in x.family:
                        if hasattr(self, a):
                            setattr(x, a, getattr(self, a))  # Set family
                    if attr_list:
                        x.setaciattrlist(attr_list)
                        if kid_attr_list:
                            for y in kid_attr_list:
                                if hasattr(x, y):
                                    setattr(self, y, getattr(x, y))
                    list.append(x)
            setattr(self, name, list)
    def setparentattr(self, parent, attrname, attr):
        if hasattr(parent, attr):
            setattr(self, attrname, getattr(parent, attr))

    def setsinglechildattr(self, attrchild, newattrname, attr): # Note returns last child attr in list
        if hasattr(self, attrchild):
            tmp = getattr(self, attrchild)
            for a in tmp:
                if hasattr(a, attr):
                    tmp1 = getattr(a, attr)
                    setattr(self, newattrname, getattr(a, attr))



    '''def setFamilyTree(self, child, family_tree = []):
        ### family_tree is a list of objects for grandparents and great-grandparents
        if hasattr(parent, self.type):
            for z in getattr(parent, self.type):
                setattr(z, parent.type, parent.name)
                if family_tree:
                    for a in family_tree:
                        setattr(z, a.type, a.name)
                if kid_list:
                    for a in kid_list:
                        setattr(z, a.type, a.name)'''

    def sortaci(self, key):
        self.sort(key=itemgetter(key), reverse=True)

    '''family = [kid1: {'name': 'name', 'attr': [], kidlist: []]

    def filterfamily(self, root, family):
        for a in self:
            for b in family:
                a.filterkids(family[b]['name'], 'bgpRRNodePEp', family[b]['attr'])'''