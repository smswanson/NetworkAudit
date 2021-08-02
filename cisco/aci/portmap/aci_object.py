import operator
from pprint import pprint


def getchild(parent, childkey, grandchildkey=[], grandchild=False):
    u = {'attributes': {}}
    for c in childkey:
        for z in parent['children']:
            if c in z.keys():
                u['attributes'].update(z[c]['attributes'])
                # Process Grandchild
                if grandchild:
                    for b in grandchildkey:
                        for x in z[c]['children']:
                            if b in x.keys():
                                u['attributes'].update(x[b]['attributes'])
    return u

def sortkeys(objlist,key):
    keyfun = operator.attrgetter(key) # use operator since it's faster than lambda
    objlist.sort(key=keyfun, reverse=True) # sort in-place

class AciChild:
    def __init__(self, aciObj, childkey, parentkey=''):
        self.name = childkey
        self.parent = parentkey
        self.indata = aciObj
        self.child = []
        self.data = []
        for c in self.indata['children']:
            K = c.keys()
            for i in K:
                if self.name == i:
                    t = {self.name: c[i]}
                    self.data.append(t)


class aciObj:
    def __init__(self, name='fvTenant', dict={}, topkey='imdata', headline=[], children=False,
                 childrenkey=[], children2=False, childrenkey2=[], newKey=''):
        all_data_list = dict[topkey]
        self.data = []
        self.child = []
        self.grandchild = []
        self.headline = headline
        self.name = name
        for i in all_data_list:
            # Create list of like Keys.
            t = {}
            u = {}
            v = {}
            K = list(i.keys())
            nK = K[0]
            if newKey != '':
                nK = newKey
                self.name = newKey
            if K[0] == name:
                t = {nK: i[K[0]]}
                self.data.append(t)
                '''if 'children' in i[K[0]].keys():
                    print('\n\n Found Children \n\n')
                    u = {nK: i[K[0]]['children']}
                    self.child.append(u)'''

            else:
                # print('No matching values for: ' + self.name)
                pass