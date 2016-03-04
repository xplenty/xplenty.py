from datetime import datetime
import unittest

from xplenty import models


class Obj(models.BaseModel):
    _ints = ["i"]
    _strs = ["s"]


class ModelsTestCase(unittest.TestCase):

    def test_to_python_str_keys(self):
        obj = Obj()
        data = {"a": 1, "b": "2"}
        obj = models.to_python(obj, data, str_keys=["a", "b"])
        self.assertEqual(obj.a, "1")
        self.assertEqual(obj.b, "2")

    def test_to_python_date_keys(self):
        obj = Obj()
        data = {"d": "2015-10-09 13:12:47"}
        obj = models.to_python(obj, data, date_keys=["d"])
        self.assertIsInstance(obj.d, datetime)
        self.assertEqual(obj.d, datetime(2015, 10, 9, 13, 12, 47))

    def test_to_python_date_keys_parse_error(self):
        obj = Obj()
        data = {"d": "ieoazyehiazne"}
        obj = models.to_python(obj, data, date_keys=["d"])
        self.assertIsNone(obj.d)

    def test_to_python_int_keys(self):
        obj = Obj()
        data = {"i": 12, "ii": "127"}
        obj = models.to_python(obj, data, int_keys=["i", "ii"])
        self.assertEqual(obj.i, 12)
        self.assertEqual(obj.ii, 127)

    def test_to_python_int_keys_bad_int(self):
        obj = Obj()
        data = {"iii": "ugu"}
        obj = models.to_python(obj, data, int_keys=["iii"])
        self.assertIsNone(obj.iii)

    def test_to_python_float_keys(self):
        obj = Obj()
        data = {"f": 12.9, "ff": "127.98"}
        obj = models.to_python(obj, data, float_keys=["f", "ff"])
        self.assertEqual(obj.f, 12.9)
        self.assertEqual(obj.ff, 127.98)

    def test_to_python_float_keys_bad_float(self):
        obj = Obj()
        data = {"fff": "eazeazeaz"}
        obj = models.to_python(obj, data, float_keys=["fff"])
        self.assertIsNone(obj.fff)

    def test_to_python_object_map(self):
        obj = Obj()
        data = {"obj": {"i": "3", "s": "uhu"}}
        obj = models.to_python(obj, data, object_map={"obj": Obj})
        self.assertIsInstance(obj.obj, Obj)
        self.assertEqual(obj.obj.i, 3)
        self.assertEqual(obj.obj.s, "uhu")

    def test_to_python_object_map_list(self):
        obj = Obj()
        data = {"objs": [{"i": "3", "s": "uhu"}, {"i": "1", "s": "aha"}]}
        obj = models.to_python(obj, data, object_map={"objs": [Obj]})
        self.assertIsInstance(obj.objs, list)
        o1, o2 = obj.objs
        self.assertEqual(o1.i, 3)
        self.assertEqual(o1.s, "uhu")
        self.assertEqual(o2.i, 1)
        self.assertEqual(o2.s, "aha")

    def test_to_python_bool_keys(self):
        obj = Obj()
        data = {"b": True, "bb": 0, "bbb": "oeihzioe"}
        obj = models.to_python(obj, data, bool_keys=["b", "bb", "bbb"])
        self.assertTrue(obj.b)
        self.assertFalse(obj.bb)
        self.assertTrue(obj.bbb)

    def test_to_python_dict_keys(self):
        obj = Obj()
        data = {"d": {"key": "value"}}
        obj = models.to_python(obj, data, dict_keys=["d"])
        self.assertEqual(obj.d, {"key": "value"})

    def test_to_python_list_keys(self):
        obj = Obj()
        data = {"l": ["a1", "a2"]}
        obj = models.to_python(obj, data, list_keys=["l"])
        self.assertEqual(obj.l, ["a1", "a2"])

    def test_to_python_kwargs(self):
        obj = Obj()
        data = {}
        obj = models.to_python(obj, data, key="value")
        self.assertEqual(obj.key, "value")
