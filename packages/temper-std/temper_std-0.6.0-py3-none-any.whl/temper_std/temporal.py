from temper_std.json import JsonAdapter, JsonProducer, JsonSyntaxTree, InterchangeContext, JsonString
from datetime import date as date79
from builtins import str as str14, int as int19, bool as bool12, list as list2, len as len5
from temper_core import cast_by_type as cast_by_type57, date_to_string as date_to_string75, date_from_iso_string as date_from_iso_string76, arith_int_mod as arith_int_mod77, int_to_string as int_to_string6, string_get as string_get36, string_next as string_next38, string_count_between as string_count_between78, int_sub as int_sub20
from typing import Sequence as Sequence16
from temper_std.json import JsonAdapter, JsonString
date_to_string_2624 = date_to_string75
date_from_iso_string_2625 = date_from_iso_string76
arith_int_mod_2626 = arith_int_mod77
int_to_string_2627 = int_to_string6
len_2628 = len5
string_get_2629 = string_get36
string_next_2631 = string_next38
string_count_between_2632 = string_count_between78
int_sub_2633 = int_sub20
class DateJsonAdapter_109(JsonAdapter['date79']):
    __slots__ = ()
    def encode_to_json(this_120, x_116: 'date79', p_117: 'JsonProducer') -> 'None':
        encode_to_json_90(x_116, p_117)
    def decode_from_json(this_121, t_118: 'JsonSyntaxTree', ic_119: 'InterchangeContext') -> 'date79':
        return decode_from_json_93(t_118, ic_119)
    def __init__(this_122) -> None:
        pass
# Type `std/temporal/`.Date connected to datetime.date
def encode_to_json_90(this_20: 'date79', p_91: 'JsonProducer') -> 'None':
    t_313: 'str14' = date_to_string_2624(this_20)
    p_91.string_value(t_313)
def decode_from_json_93(t_94: 'JsonSyntaxTree', ic_95: 'InterchangeContext') -> 'date79':
    t_190: 'JsonString'
    t_190 = cast_by_type57(t_94, JsonString)
    return date_from_iso_string_2625(t_190.content)
def json_adapter_124() -> 'JsonAdapter[date79]':
    return DateJsonAdapter_109()
days_in_month_34: 'Sequence16[int19]' = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
def is_leap_year_32(year_41: 'int19') -> 'bool12':
    return_21: 'bool12'
    t_263: 'int19'
    if arith_int_mod_2626(year_41, 4) == 0:
        if arith_int_mod_2626(year_41, 100) != 0:
            return_21 = True
        else:
            t_263 = arith_int_mod_2626(year_41, 400)
            return_21 = t_263 == 0
    else:
        return_21 = False
    return return_21
def pad_to_33(min_width_43: 'int19', num_44: 'int19', sb_45: 'list2[str14]') -> 'None':
    "If the decimal representation of \\|num\\| is longer than [minWidth],\nthen appends that representation.\nOtherwise any sign for [num] followed by enough zeroes to bring the\nwhole length up to [minWidth].\n\n```temper\n// When the width is greater than the decimal's length,\n// we pad to that width.\n\"0123\" == do {\n  let sb = new StringBuilder();\n  padTo(4, 123, sb);\n  sb.toString()\n}\n\n// When the width is the same or lesser, we just use the string form.\n\"123\" == do {\n  let sb = new StringBuilder();\n  padTo(2, 123, sb);\n  sb.toString()\n}\n\n// The sign is always on the left.\n\"-01\" == do {\n  let sb = new StringBuilder();\n  padTo(3, -1, sb);\n  sb.toString()\n}\n```\n\nminWidth__43: Int32\n\nnum__44: Int32\n\nsb__45: builtins.list<String>\n"
    t_346: 'int19'
    t_348: 'int19'
    t_257: 'bool12'
    decimal_47: 'str14' = int_to_string_2627(num_44, 10)
    decimal_index_48: 'int19' = 0
    decimal_end_49: 'int19' = len_2628(decimal_47)
    if decimal_index_48 < decimal_end_49:
        t_346 = string_get_2629(decimal_47, decimal_index_48)
        t_257 = t_346 == 45
    else:
        t_257 = False
    if t_257:
        sb_45.append('-')
        t_348 = string_next_2631(decimal_47, decimal_index_48)
        decimal_index_48 = t_348
    t_349: 'int19' = string_count_between_2632(decimal_47, decimal_index_48, decimal_end_49)
    n_needed_50: 'int19' = int_sub_2633(min_width_43, t_349)
    while n_needed_50 > 0:
        sb_45.append('0')
        n_needed_50 = int_sub_2633(n_needed_50, 1)
    sb_45.append(decimal_47[decimal_index_48 : decimal_end_49])
day_of_week_lookup_table_leapy_35: 'Sequence16[int19]' = (0, 0, 3, 4, 0, 2, 5, 0, 3, 6, 1, 4, 6)
day_of_week_lookup_table_not_leapy_36: 'Sequence16[int19]' = (0, 0, 3, 3, 6, 1, 4, 6, 2, 5, 0, 3, 5)
