from numbers import Number

class PdbRecord:
    """A PdbRecord represents a single line in a PDB file. As such, it follows
    the same constraints that the PDB file formats impose on the lines in the
    actual files - namely that it cannot be more than 80 characters.

    Two PdbRecords are considered equal if they have the same text.

    PdbRecords are containers and iterables, in the same way that strings are.

    Also like strings you can index them using ``record[x:y]`` notation, but in
    order to aid parsing, they will process the substring before returning it
    It will strip whitespace from the substring, attempt to convert it to an
    int or a float, and return None if an empty string would be returned. It
    will also treat the record as an 80 character string, regardless of the
    actual length of the record. If this is more of an annoyance than a
    convenience, you can use :py:meth:`.get_as_string`, which works just like
    regualar indexing.

    :param str text: The string contents of the line in the PDB file.
    :raises ValueError: if a string longer than 80 characters is supplied."""

    def __init__(self, text):
        if not isinstance(text, str):
            raise TypeError("PdbRecord needs str, not '%s'" % str(text))
        if len(text) > 80:
            raise ValueError("'%s' is longer than 80 characters" % str(text))
        self._text = text.rstrip()


    def __repr__(self):
        return "<{} record>".format(self.name())


    def __eq__(self, other):
        return isinstance(other, PdbRecord) and self._text == other._text


    def __len__(self):
        return len(self._text)


    def __contains__(self, member):
        return member in self._text


    def __iter__(self):
        return iter(self._text)


    def __getitem__(self, index):
        full_line = self._text + (" " * (80 - len(self._text)))
        chunk = full_line[index].strip()
        try:
            chunk = int(chunk)
        except ValueError:
            try:
                chunk = float(chunk)
            except ValueError:
                pass
        if chunk or isinstance(chunk, Number): return chunk
        return None


    def get_as_string(self, index, index2=None):
        """Indexing a PdbRecord will process the resultant substring in various
        ways, such as by converting it to an int or float. If you just want the
        string regardless, you can use this method to force a straight string
        return.

        :param int index: the index of the text you wish to get.
        :param int index2: if given, a slice will be taken using the two indeces."""

        full_line = self._text + (" " * (80 - len(self._text)))
        if index2:
            return full_line[index: index2]
        return full_line[index]


    def text(self, text=None):
        """The full string of the record. If a string is passed as an argument,
        the text will be updated, though any trailing whitespace will be
        removed.

        :param str text: If given, the record's text will be updated to this.
        :raises ValueError: if a string longer than 80 characters is supplied."""

        if text is None:
            return self._text
        else:
            if not isinstance(text, str):
                raise TypeError("PdbRecord needs str, not '%s'" % str(text))
            if len(text) > 80:
                raise ValueError("'%s' is longer than 80 characters" % str(text))
            self._text = text.rstrip()


    def name(self, name=None):
        """The name of the record, given by the first six characters of the line
        in the PDB file. The name will have any whitespace removed. If a string
        is passed as an argument, the name will be updated.

        :param str name: If given, the record's name will be updated to this.
        :raises ValueError: if a string longer than 6 characters is supplied."""

        if name is None:
            return self._text[:6].strip()
        else:
            if not isinstance(name, str):
                raise TypeError("PdbRecord needs str, not '%s'" % str(name))
            if len(name) > 6:
                raise ValueError("'%s' is longer than 6 characters" % str(name))
            self._text = name + (" " * (6 - len(name))) + self._text[6:]


    def body(self, body=None):
        """The body of the record - everything from column seven onwards (after
        the name). If a string is passed as an argument, the body will be
        updated, though any trailing whitespace will be removed.

        :param str body: If given, the record's body will be updated to this.
        :raises ValueError: if a string longer than 74 characters is supplied."""

        if body is None:
            return self._text[6:]
        else:
            if not isinstance(body, str):
                raise TypeError("PdbRecord needs str, not '%s'" % str(body))
            if len(body) > 74:
                raise ValueError("'%s' is longer than 74 characters" % str(body))
            self._text = self._text[:6] + body.rstrip()