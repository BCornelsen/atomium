from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from atomium.files.pdbdict2pdbstring import *

class PdbDictToPdbStringTests(TestCase):

    @patch("atomium.files.pdbdict2pdbstring.pack_header")
    @patch("atomium.files.pdbdict2pdbstring.pack_structure")
    @patch("atomium.files.utilities.lines_to_string")
    def test_can_convert_pdb_dict_to_string(self, mock_str, mock_struct, mock_head):
        pdb_dict = {"pdb": "dict"}
        mock_str.return_value = "filestring"
        filestring = pdb_dict_to_pdb_string(pdb_dict)
        mock_head.assert_called_with([], pdb_dict)
        mock_struct.assert_called_with([], pdb_dict)
        mock_str.assert_called_with([])
        self.assertEqual(filestring, "filestring")



class HeaderPackingTests(TestCase):

    def setUp(self):
        self.pdb_dict = {
         "deposition_date": datetime(1990, 9, 1).date(),
         "code": "1XYZ", "title": "ABC" * 40
        }
        self.lines = []


    def test_can_pack_full_header(self):
        pack_header(self.lines, self.pdb_dict)
        self.assertEqual(self.lines, [
         "HEADER" + " " * 44 + "01-SEP-90   1XYZ" + " " * 14,
         "TITLE     " + "ABC" * 23 + "A",
         "TITLE    2 " + "BC" + "ABC" * 16 + " " * 19
        ])


    def test_can_pack_deposition_date(self):
        self.pdb_dict["code"], self.pdb_dict["title"] = None, None
        pack_header(self.lines, self.pdb_dict)
        self.assertEqual(self.lines, [
         "HEADER" + " " * 44 + "01-SEP-90       " + " " * 14,
        ])


    def test_can_pack_code(self):
        self.pdb_dict["deposition_date"], self.pdb_dict["title"] = None, None
        pack_header(self.lines, self.pdb_dict)
        self.assertEqual(self.lines, [
         "HEADER" + " " * 44 + "            1XYZ" + " " * 14,
        ])


    def test_can_pack_title(self):
        self.pdb_dict["deposition_date"], self.pdb_dict["code"] = None, None
        pack_header(self.lines, self.pdb_dict)
        self.assertEqual(self.lines, [
         "TITLE     " + "ABC" * 23 + "A",
         "TITLE    2 " + "BC" + "ABC" * 16 + " " * 19
        ])



class StructurePackingTests(TestCase):

    def setUp(self):
        self.pdb_dict = {
         "models": [{"model": 1}],
         "connections": [{"connection": 1}, {"connection": 2}]
        }
        self.lines = []


    @patch("atomium.files.pdbdict2pdbstring.pack_model")
    @patch("atomium.files.pdbdict2pdbstring.pack_connections")
    def test_can_pack_structure_one_model(self, mock_con, mock_model):
        pack_structure(self.lines, self.pdb_dict)
        mock_model.assert_called_with([], {"model": 1}, sole=True)
        mock_con.assert_called_with([], self.pdb_dict)


    @patch("atomium.files.pdbdict2pdbstring.pack_model")
    @patch("atomium.files.pdbdict2pdbstring.pack_connections")
    def test_can_pack_structure_multiple_models(self, mock_con, mock_model):
        self.pdb_dict["models"] += [{"model": 2}, {"model": 3}]
        pack_structure(self.lines, self.pdb_dict)
        mock_model.assert_any_call([], {"model": 1})
        mock_model.assert_any_call([], {"model": 2})
        mock_model.assert_any_call([], {"model": 3})
        mock_con.assert_called_with([], self.pdb_dict)



class ModelPackingTests(TestCase):

    def setUp(self):
        self.model_dict = {
         "chains": [
          {"residues": [{"atoms": ["r11", "r12"]}, {"atoms": ["r21", "r22"]}]},
          {"residues": [{"atoms": ["r31", "r32"]}, {"atoms": ["r41", "r42"]}]},
         ],
         "molecules": [
          {"atoms": ["m11", "m12"]}, {"atoms": ["m21", "m22"]},
          {"atoms": ["m31", "m32"]}, {"atoms": ["m41", "m42"]}
         ]
        }
        self.lines = []


    @patch("atomium.files.pdbdict2pdbstring.atom_dict_to_atom_line")
    def test_can_pack_sole_model(self, mock_line):
        mock_line.side_effect = ["a" + str(i) for i in range(16)]
        pack_model(self.lines, self.model_dict, sole=True)
        for char in ["r", "m"]:
            for num1 in ["1", "2", "3", "4"]:
                for num2 in ["1", "2"]:
                    mock_line.assert_any_call(
                     char + num1 + num2, hetero=char == "m"
                    )
        self.assertEqual(self.lines, [
         "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
         "a8", "a9", "a10", "a11", "a12", "a13", "a14", "a15"
        ])


    @patch("atomium.files.pdbdict2pdbstring.atom_dict_to_atom_line")
    def test_can_pack_model_in_series(self, mock_line):
        mock_line.side_effect = ["a" + str(i) for i in range(16)]
        pack_model(self.lines, self.model_dict)
        for char in ["r", "m"]:
            for num1 in ["1", "2", "3", "4"]:
                for num2 in ["1", "2"]:
                    mock_line.assert_any_call(
                     char + num1 + num2, hetero=char == "m"
                    )
        self.assertEqual(self.lines, [
         "MODEL".ljust(80), "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
         "a8", "a9", "a10", "a11", "a12", "a13", "a14", "a15", "ENDMDL".ljust(80)
        ])



class AtomDictToAtomLineTests(TestCase):

    def setUp(self):
        self.atom_dict = {
         "atom_id": 107, "atom_name": "N", "alt_loc": "A",
         "residue_name": "GLY",
         "chain_id": "B", "residue_id": 13, "insert_code": "C",
         "x": 12.681, "y": 37.302, "z": -25.211,
         "occupancy": 0.5, "temp_factor": 15.56,
         "element": "N", "charge": -2
        }


    def test_can_convert_empty_atom_dict_to_line(self):
        for key in self.atom_dict:
            self.atom_dict[key] = None
        self.atom_dict["chain_id"], self.atom_dict["insert_code"] = "", ""
        self.atom_dict["occupancy"], self.atom_dict["charge"] = 1, 0
        self.assertEqual(
         atom_dict_to_atom_line(self.atom_dict),
         "ATOM".ljust(80)
        )


    def test_can_convert_full_atom_dict_to_line(self):
        line = atom_dict_to_atom_line(self.atom_dict)
        self.assertEqual(line[:30], "ATOM    107  N  AGLY B  13C   ")
        self.assertEqual(line[30:54], "  12.681  37.302 -25.211")
        self.assertEqual(line[54:80], "  0.50 15.56           N2-")


    def test_can_handle_different_atom_name_sizes(self):
        self.atom_dict["atom_name"] = "CA"
        line = atom_dict_to_atom_line(self.atom_dict)
        self.assertEqual(line[:30], "ATOM    107  CA AGLY B  13C   ")
        self.atom_dict["atom_name"] = "CG2"
        line = atom_dict_to_atom_line(self.atom_dict)
        self.assertEqual(line[:30], "ATOM    107  CG2AGLY B  13C   ")
        self.atom_dict["atom_name"] = "HCG2"
        line = atom_dict_to_atom_line(self.atom_dict)
        self.assertEqual(line[:30], "ATOM    107 HCG2AGLY B  13C   ")


    def test_can_convert_heteroatom_dict_to_line(self):
        line = atom_dict_to_atom_line(self.atom_dict, hetero=True)
        self.assertEqual(line[:30], "HETATM  107  N  AGLY B  13C   ")
        self.assertEqual(line[30:54], "  12.681  37.302 -25.211")
        self.assertEqual(line[54:80], "  0.50 15.56           N2-")



class ConnectionsPackingTests(TestCase):

    def test_can_pack_connections(self):
        pdb_dict = {"connections": [{
         "atom": 1179, "bond_to": [746, 1184, 1195, 1203, 1211, 1222]
        }, {
         "atom": 1221, "bond_to": [544, 1017, 1020, 1022]
        }]}
        lines = []
        pack_connections(lines, pdb_dict)
        self.assertEqual(lines, [
         "CONECT 1179  746 1184 1195 1203".ljust(80),
         "CONECT 1179 1211 1222".ljust(80),
         "CONECT 1221  544 1017 1020 1022".ljust(80)
        ])
