# -*- coding: utf-8 -*-
import unittest
from hypothesis import given
from hypothesis.strategies import (
    binary,
    booleans,
    floats,
    integers,
    just,
    lists,
    text,
    tuples,
)


import bpickle


class BPickleTest(unittest.TestCase):

    @given(integers())
    def test_int(self, i):
        assert bpickle.loads(bpickle.dumps(i)) == i

    def test_float(self):
        self.assertAlmostEquals(bpickle.loads(bpickle.dumps(2.3)), 2.3)

    def test_float_scientific_notation(self):
        number = 0.00005
        self.assertTrue("e" in repr(number))
        self.assertAlmostEquals(bpickle.loads(bpickle.dumps(number)), number)

    @given(binary())
    def test_bytes(self, s):
        assert bpickle.loads(bpickle.dumps(s)) == s

    @given(int_value=integers(), bytes_value=binary(), unicode_value=text(),
           float_value=floats(allow_nan=False, allow_infinity=False))
    def test_list(self, int_value, bytes_value, unicode_value, float_value):
        self.assertEqual(
            bpickle.loads(bpickle.dumps(
                [int_value, unicode_value, bytes_value, float_value])),
            [int_value, unicode_value, bytes_value, float_value])

    @given(lists(integers()))
    def test_inverted_lists(self, l):
        assert bpickle.loads(bpickle.dumps(l)) == l

    @given(int_value=integers(), bytes_value=binary(), unicode_value=text(),
           float_value=floats(allow_nan=False, allow_infinity=False))
    def test_tuple(self, int_value, bytes_value, unicode_value, float_value):
        data = bpickle.dumps(
            (int_value, [], unicode_value, bytes_value, float_value))
        self.assertEqual(
            bpickle.loads(data),
            (int_value, [], unicode_value, bytes_value, float_value))

    def test_none(self):
        self.assertEqual(bpickle.loads(bpickle.dumps(None)), None)

    def test_unicode(self):
        dumped_unicode = bpickle.dumps(u'\N{SNOWMAN}')
        loaded_unicode = bpickle.loads(dumped_unicode)
        self.assertEqual(u'☃', loaded_unicode)

    @given(booleans())
    def test_bool(self, boolean):
        self.assertEqual(bpickle.loads(bpickle.dumps(boolean)), boolean)

    def test_dict(self):
        dumped_tostr = bpickle.dumps({True: u"hello"})
        self.assertEqual(bpickle.loads(dumped_tostr),
                         {True: u"hello"})
        dumped_tobool = bpickle.dumps({True: False})
        self.assertEqual(bpickle.loads(dumped_tobool),
                         {True: False})

    def test_long(self):
        long_value = 99999999999999999999999999999
        self.assertEqual(bpickle.loads(bpickle.dumps(long_value)), long_value)

    def test_loads_empty_string(self):
        self.assertRaises(ValueError, bpickle.loads, b"")

    def test_dumps_unsupported_object(self):
        class something(object):
            pass
        self.assertRaises(ValueError, bpickle.dumps, something())

    def test_loads_unknown_character(self):
        wrong = b'zblah'  # 'z' is not a valid type character.
        self.assertRaises(ValueError, bpickle.loads, wrong)

    def test_loads_broken_data(self):
        """
        If loads table somehow ends up using load function that does not
        return a tuple of value and position, ValueError is thrown.
        """
        loads_table = {b"s": lambda self, obj: []}
        with self.assertRaises(ValueError) as context:
            bpickle.loads(b"s3:foo", loads_table)
        self.assertEqual("Corrupted data", str(context.exception))

    def test_ping_result_message_decode(self):
        """
        This is an example message received from an actual ping server. Let's
        try to make sense of it.
        """
        repsonse = b'ds8:messagesb1;'  # As returned by the "requests" lib
        result = bpickle.loads(repsonse)
        expected = {b"messages": True}
        self.assertEqual(expected, result)

    def test_ping_result_message_encode(self):
        """Let's ensure the encoding/decoding is symmetric "by hand"."""
        payload = {b"messages": True}
        expected = b'ds8:messagesb1;'
        result = bpickle.dumps(payload)
        self.assertEqual(expected, result)

    def test_real_registration_answer_loading(self):
        """ We succeed at decoding a real-world example."""
        REAL_ANSWER = (
            b"ds8:messageslds4:types14:accepted-typess5:typeslu8:register"
            b"u4:test;;ds2:ids9:secure-ids11:insecure-idi999999;s4:types6:"
            b"set-id;;s10:server-apiu3:3.3s11:server-uuids11:server-uuid;")

        expected = {
            b'server-api': u'3.3',
            b'server-uuid': b'server-uuid',
            b'messages': [
                {b'types': [u'register', u'test'], b'type': b'accepted-types'},
                {b'id': b'secure-id', b'insecure-id': 999999,
                 b'type': b'set-id'}]}

        result = bpickle.loads(REAL_ANSWER)
        self.assertEqual(expected, result)
