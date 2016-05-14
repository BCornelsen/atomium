class PdbRecord:

    def __init__(self, line, number):
        self.number = number
        self.text = line.ljust(80)
        self.name = self.text[:6].strip()
        self.contents = self.text[6:]


    def __repr__(self):
        return "<PdbRecord (%s)>" % self.name


    def __getitem__(self, key):
        chunk = self.text[key].strip()
        if not chunk: return None
        if chunk.count(".") == 1:
            try:
                return float(chunk)
            except ValueError:
                pass
        try:
            return int(chunk)
        except ValueError:
            return chunk


    def get_as_string(self, start, end):
        splice = self[start:end]
        return str(splice) if splice is not None else None