import unittest
from uavcan import transport
from uavcan.dsdl import parser


class TestBitsFromBytes(unittest.TestCase):
    def test_empty(self):
        bits = transport.bits_from_bytes(bytearray(""))
        self.assertEqual(bits, "")

    def test_single_byte(self):
        bits = transport.bits_from_bytes(bytearray("\x00"))
        self.assertEqual(bits, "00000000")

        bits = transport.bits_from_bytes(bytearray("\xA5"))
        self.assertEqual(bits, "10100101")

        bits = transport.bits_from_bytes(bytearray("\xFF"))
        self.assertEqual(bits, "11111111")

        bits = transport.bits_from_bytes(bytearray("\x0F"))
        self.assertEqual(bits, "00001111")

        bits = transport.bits_from_bytes(bytearray("\xF0"))
        self.assertEqual(bits, "11110000")

    def test_multiple_bytes(self):
        bits = transport.bits_from_bytes(bytearray("\x00\xFF"))
        self.assertEqual(bits, "0000000011111111")

        bits = transport.bits_from_bytes(bytearray("\xFF\x00"))
        self.assertEqual(bits, "1111111100000000")

        bits = transport.bits_from_bytes(bytearray("\x00\x00\xAA\x55\xFF\xFF"))
        self.assertEqual(
            bits, "000000000000000010101010010101011111111111111111")


class TestBytesFromBits(unittest.TestCase):
    def test_empty(self):
        result_bytes = transport.bytes_from_bits("")
        self.assertEqual(result_bytes, b"")

    def test_partial_byte(self):
        result_bytes = transport.bytes_from_bits("0")
        self.assertEqual(result_bytes, b"\x00")

        result_bytes = transport.bytes_from_bits("1")
        self.assertEqual(result_bytes, b"\x01")

        result_bytes = transport.bytes_from_bits("100")
        self.assertEqual(result_bytes, b"\x04")

        result_bytes = transport.bytes_from_bits("001")
        self.assertEqual(result_bytes, b"\x01")

        result_bytes = transport.bytes_from_bits("1001")
        self.assertEqual(result_bytes, b"\x09")

        result_bytes = transport.bytes_from_bits("01001")
        self.assertEqual(result_bytes, b"\x09")

        result_bytes = transport.bytes_from_bits("0001001")
        self.assertEqual(result_bytes, b"\x09")

        result_bytes = transport.bytes_from_bits("1001001")
        self.assertEqual(result_bytes, b"\x49")

    def test_single_byte(self):
        result_bytes = transport.bytes_from_bits("10010110")
        self.assertEqual(result_bytes, b"\x96")

        result_bytes = transport.bytes_from_bits("10100101")
        self.assertEqual(result_bytes, b"\xA5")

        result_bytes = transport.bytes_from_bits("00000000")
        self.assertEqual(result_bytes, b"\x00")

    def test_multiple_bytes(self):
        result_bytes = transport.bytes_from_bits("1010010110010110")
        self.assertEqual(result_bytes, b"\xA5\x96")

        result_bytes = transport.bytes_from_bits("11010010110010110")
        self.assertEqual(result_bytes, b"\xD2\xCB\x00")

        result_bytes = transport.bytes_from_bits("10100101100101101")
        self.assertEqual(result_bytes, b"\xA5\x96\x01")


class TestBEFromLEBits(unittest.TestCase):
    def test_partial_byte(self):
        for bits in ("0", "1", "100", "001", "1001", "01001", "001001",
                     "1001001"):
            out_bits = transport.be_from_le_bits(bits, len(bits))
            self.assertEqual(out_bits, bits)

    def test_single_byte(self):
        for bits in ("10010110", "10100101", "00000000"):
            out_bits = transport.be_from_le_bits(bits, 8)
            self.assertEqual(out_bits, bits)

    def test_multiple_bytes(self):
        #                                     llllllllmmmm
        out_bits = transport.be_from_le_bits("110110101110", 12)
        #                                     mmmmllllllll
        self.assertEqual(out_bits,          b"111011011010")

        #                                     llllllllmmmmmmmm
        out_bits = transport.be_from_le_bits("1010010110010110", 16)
        #                                     mmmmmmmmllllllll
        self.assertEqual(out_bits,          b"1001011010100101")

        #                                     llllllll........m
        out_bits = transport.be_from_le_bits("11010010110010110", 17)
        #                                     m........llllllll
        self.assertEqual(out_bits,          b"01100101111010010")

        #                                     llllllll........m
        out_bits = transport.be_from_le_bits("10100101100101101", 17)
        #                                     m........llllllll
        self.assertEqual(out_bits,          b"11001011010100101")


class TestLEFromBEBits(unittest.TestCase):
    def test_partial_byte(self):
        for bits in ("0", "1", "100", "001", "1001", "01001", "001001",
                     "1001001"):
            out_bits = transport.le_from_be_bits(bits, len(bits))
            self.assertEqual(out_bits, bits)

    def test_single_byte(self):
        for bits in ("10010110", "10100101", "00000000"):
            out_bits = transport.le_from_be_bits(bits, 8)
            self.assertEqual(out_bits, bits)

    def test_multiple_bytes(self):
        #                                     mmmmllllllll
        out_bits = transport.le_from_be_bits("111011011010", 12)
        #                                     llllllllmmmm
        self.assertEqual(out_bits,          b"110110101110")

        #                                     mmmmmmmmllllllll
        out_bits = transport.le_from_be_bits("1001011010100101", 16)
        #                                     llllllllmmmmmmmm
        self.assertEqual(out_bits,          b"1010010110010110")

        #                                     m........llllllll
        out_bits = transport.le_from_be_bits("01100101111010010", 17)
        #                                     llllllll........m
        self.assertEqual(out_bits,          b"11010010110010110")

        #                                     m........llllllll
        out_bits = transport.le_from_be_bits("11001011010100101", 17)
        #                                     llllllll........m
        self.assertEqual(out_bits,          b"10100101100101101")


class TestCast(unittest.TestCase):
    def test_truncated_1bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            1,
            parser.PrimitiveType.CAST_MODE_TRUNCATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(1, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(2, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(5, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(-10, dtype)
        self.assertEqual(value, 0)

    def test_truncated_4bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            4,
            parser.PrimitiveType.CAST_MODE_TRUNCATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(15, dtype)
        self.assertEqual(value, 15)
        value = transport.cast(16, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 15)
        value = transport.cast(30, dtype)
        self.assertEqual(value, 14)

    def test_truncated_33bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            33,
            parser.PrimitiveType.CAST_MODE_TRUNCATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(8589934591, dtype)
        self.assertEqual(value, 8589934591)
        value = transport.cast(8589934592, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 8589934591)

    def test_truncated_64bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            64,
            parser.PrimitiveType.CAST_MODE_TRUNCATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(18446744073709551615, dtype)
        self.assertEqual(value, 18446744073709551615)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 18446744073709551615)
        value = transport.cast(18446744073709551617, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(-18446744073709551615, dtype)
        self.assertEqual(value, 1)

    def test_unsigned_saturated_1bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            1,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(1, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(2, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(5, dtype)
        self.assertEqual(value, 1)
        value = transport.cast(-10, dtype)
        self.assertEqual(value, 0)

    def test_unsigned_saturated_4bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            4,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(15, dtype)
        self.assertEqual(value, 15)
        value = transport.cast(16, dtype)
        self.assertEqual(value, 15)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(30, dtype)
        self.assertEqual(value, 15)

    def test_unsigned_saturated_33bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            33,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(8589934591, dtype)
        self.assertEqual(value, 8589934591)
        value = transport.cast(8589934592, dtype)
        self.assertEqual(value, 8589934591)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 0)

    def test_unsigned_saturated_64bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_UNSIGNED_INT,
            64,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(18446744073709551615, dtype)
        self.assertEqual(value, 18446744073709551615)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(18446744073709551617, dtype)
        self.assertEqual(value, 18446744073709551615)
        value = transport.cast(-18446744073709551615, dtype)
        self.assertEqual(value, 0)

    def test_signed_saturated_4bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_SIGNED_INT,
            4,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(15, dtype)
        self.assertEqual(value, 7)
        value = transport.cast(16, dtype)
        self.assertEqual(value, 7)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, -1)
        value = transport.cast(-30, dtype)
        self.assertEqual(value, -8)

    def test_signed_saturated_33bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_SIGNED_INT,
            33,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(8589934591, dtype)
        self.assertEqual(value, 4294967295)
        value = transport.cast(-8589934592, dtype)
        self.assertEqual(value, -4294967296)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, -1)

    def test_signed_saturated_64bit(self):
        dtype = parser.PrimitiveType(
            parser.PrimitiveType.KIND_SIGNED_INT,
            64,
            parser.PrimitiveType.CAST_MODE_SATURATED)
        value = transport.cast(0, dtype)
        self.assertEqual(value, 0)
        value = transport.cast(18446744073709551615, dtype)
        self.assertEqual(value, 9223372036854775808)
        value = transport.cast(-1, dtype)
        self.assertEqual(value, -1)
        value = transport.cast(-18446744073709551617, dtype)
        self.assertEqual(value, -9223372036854775809)
        value = transport.cast(-9223372036854775808, dtype)
        self.assertEqual(value, -9223372036854775808)

    def test_float16_truncated(self):
        pass

    def test_float16_saturated(self):
        pass

    def test_float32_truncated(self):
        pass

    def test_float32_saturated(self):
        pass


class TestArrayBasic(unittest.TestCase):
    def setUp(self):
        custom_type = parser.CompoundType(
            "CustomType",
            parser.CompoundType.KIND_MESSAGE,
            "source.uavcan",
            0,
            ""
        )
        custom_type.fields = [
            parser.Field(
                parser.PrimitiveType(
                    parser.PrimitiveType.KIND_SIGNED_INT,
                    8,
                    parser.PrimitiveType.CAST_MODE_TRUNCATED
                ),
                "a"
            ),
            parser.Field(
                parser.PrimitiveType(
                    parser.PrimitiveType.KIND_FLOAT,
                    16,
                    parser.PrimitiveType.CAST_MODE_SATURATED
                ),
                "b"
            ),
            parser.Field(
                parser.ArrayType(
                    parser.PrimitiveType(
                        parser.PrimitiveType.KIND_UNSIGNED_INT,
                        1,
                        parser.PrimitiveType.CAST_MODE_SATURATED
                    ),
                    parser.ArrayType.MODE_DYNAMIC,
                    5
                ),
                "c"
            )
        ]
        def custom_type_factory(*args, **kwargs):
            return transport.CompoundValue(custom_type, tao=True, *args, **kwargs)
        custom_type.__call__ = custom_type_factory

        self.a1_type = parser.ArrayType(
            parser.PrimitiveType(
                parser.PrimitiveType.KIND_SIGNED_INT,
                8,
                parser.PrimitiveType.CAST_MODE_TRUNCATED
            ),
            parser.ArrayType.MODE_STATIC,
            4
        )
        self.a2_type = parser.ArrayType(
            parser.PrimitiveType(
                parser.PrimitiveType.KIND_FLOAT,
                16,
                parser.PrimitiveType.CAST_MODE_SATURATED
            ),
            parser.ArrayType.MODE_STATIC,
            2
        )
        self.a3_type = parser.ArrayType(
            custom_type,
            parser.ArrayType.MODE_STATIC,
            2
        )

    def test_size(self):
        self.assertEqual(self.a3_type.value_type.fields[2].type.value_type.bitlen, 1)
        self.assertEqual(self.a1_type.get_max_bitlen(), 8 * 4)
        self.assertEqual(self.a2_type.get_max_bitlen(), 16 * 2)
        self.assertEqual(self.a3_type.get_max_bitlen(), (8 + 16 + 5 + 3) * 2)

    def test_representation(self):
        a1 = transport.ArrayValue(self.a1_type, tao=False)
        a2 = transport.ArrayValue(self.a2_type, tao=False)
        a3 = transport.ArrayValue(self.a3_type, tao=True)
        for i in xrange(4):
            a1[i] = i
        for i in xrange(2):
            a2[i] = i
        for i in xrange(2):
            a3[i].a = i
            a3[i].b = i
            for i2 in xrange(5):
                a3[i].c.append(i2 & 1)
            self.assertEqual(len(a3[i].c), 5)

        self.assertEqual(
            transport.format_bits(a1.pack()),
            "00000000 00000001 00000010 00000011"
        )
        self.assertEqual(
            transport.format_bits(a2.pack()),
            "00000000 00000000 00000000 00111100"
        )
        self.assertEqual(
            transport.format_bits(a3.pack()),
            "00000000 00000000 00000000 10101010 " +
            "00000001 00000000 00111100 10101010"
        )


class TestVoid(unittest.TestCase):
    def setUp(self):
        self.custom_type = parser.CompoundType(
            "CustomType",
            parser.CompoundType.KIND_MESSAGE,
            "source.uavcan",
            0,
            ""
        )
        self.custom_type.fields = [
            parser.Field(
                parser.PrimitiveType(
                    parser.PrimitiveType.KIND_FLOAT,
                    16,
                    parser.PrimitiveType.CAST_MODE_SATURATED
                ),
                "a"
            ),
            parser.Field(parser.VoidType(3), None),
            parser.Field(
                parser.PrimitiveType(
                    parser.PrimitiveType.KIND_UNSIGNED_INT,
                    1,
                    parser.PrimitiveType.CAST_MODE_SATURATED
                ),
                "b"
            )
        ]
        def custom_type_factory(*args, **kwargs):
            return transport.CompoundValue(self.custom_type, tao=True, *args,
                                           **kwargs)
        self.custom_type.__call__ = custom_type_factory

    def test_size(self):
        self.assertEqual(self.custom_type.fields[1].type.bitlen, 3)
        self.assertEqual(self.custom_type.get_max_bitlen(), 20)

    def test_representation(self):
        c1 = self.custom_type()
        self.assertEqual(
            transport.format_bits(c1.pack()),
            "00000000 00000000 0000"
        )

        c1.a = 1
        c1.b = 1
        self.assertEqual(
            transport.format_bits(c1.pack()),
            "00000000 00111100 0001"
        )


class TestMessageUnion(unittest.TestCase):
    def setUp(self):
        self.custom_type = parser.CompoundType(
            "CustomType",
            parser.CompoundType.KIND_MESSAGE,
            "source.uavcan",
            0,
            ""
        )
        self.custom_type.union = True
        self.custom_type.fields = [
            parser.Field(
                parser.PrimitiveType(
                    parser.PrimitiveType.KIND_FLOAT,
                    16,
                    parser.PrimitiveType.CAST_MODE_SATURATED
                ),
                "a"
            ),
            parser.Field(
                parser.ArrayType(
                    parser.PrimitiveType(
                        parser.PrimitiveType.KIND_UNSIGNED_INT,
                        8,
                        parser.PrimitiveType.CAST_MODE_SATURATED
                    ),
                    parser.ArrayType.MODE_STATIC,
                    2
                ),
                "b"
            )
        ]
        def custom_type_factory(*args, **kwargs):
            return transport.CompoundValue(self.custom_type, tao=True, *args,
                                           **kwargs)
        self.custom_type.__call__ = custom_type_factory

    def test_size(self):
        self.assertEqual(self.custom_type.fields[0].type.bitlen, 16)
        self.assertEqual(self.custom_type.fields[1].type.get_max_bitlen(), 16)
        self.assertEqual(self.custom_type.get_max_bitlen(), 17)

    def test_representation(self):
        c1 = self.custom_type()
        self.assertEqual(
            transport.format_bits(c1.pack()),
            "00000000 00000000 0"
        )

        c2 = self.custom_type()
        c2.a = 1
        self.assertEqual(c2.union_field, "a")
        self.assertEqual(
            transport.format_bits(c2.pack()),
            "00000000 00011110 0"
        )

        c3 = self.custom_type()
        c3.b[0] = 1
        c3.b[1] = 3
        self.assertEqual(c3.union_field, "b")
        self.assertEqual(
            transport.format_bits(c3.pack()),
            "10000000 10000001 1"
        )


if __name__ == '__main__':
    unittest.main()
