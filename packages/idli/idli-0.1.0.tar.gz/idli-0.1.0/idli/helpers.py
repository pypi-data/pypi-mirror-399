

class AutoInt:
    pass


class AutoUUID:
    pass


class BTreeIndex:

    def __init__(self, *args):
        self.columns = list(args)


    @property
    def name_hash(self):
        return '_'.join(map(
            lambda x: 'd' + x[1:] if x.startswith('-') else 'a' + x,
            self.columns
        )) + '_btree'


class PrimaryKey:

    def  __init__(self, *args):
        self.columns = list(args)
