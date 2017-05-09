"""Contains classes for structures made of atoms."""

from .atoms import Atom

class AtomicStructure:
    """Represents structures made of :py:class:`.Atom`s, which tends to be
    rather a lot of things in practice. This class would not generally be
    instantiated directly, and is here to be a parent class to other, more
    specific entities.

    AtomicStructures are containers of their atoms.

    :param \*atoms: The :py:class:`.Atom`s that make up the structure.
    :raises TypeError: if non-atoms are given."""

    def __init__(self, *atoms):
        if not all(isinstance(atom, Atom) for atom in atoms):
            non_atoms = [atom for atom in atoms if not isinstance(atom, Atom)]
            raise TypeError(
             "AtomicStructures need atoms, not '{}'".format(non_atoms[0])
            )
        self._atoms = set(atoms)


    def __repr__(self):
        return "<AtomicStructure ({} atoms)>".format(len(self._atoms))


    def __contains__(self, member):
        return member in self._atoms