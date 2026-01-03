from abc import ABCMeta as ABCMeta48
from builtins import str as str14, bool as bool12, int as int19, list as list2, isinstance as isinstance56, len as len5, tuple as tuple0
from typing import Callable as Callable15, Sequence as Sequence16, Union as Union17, Any as Any58, ClassVar as ClassVar50, MutableSequence as MutableSequence13
from types import MappingProxyType as MappingProxyType53
from temper_core import cast_by_type as cast_by_type57, Label as Label55, Pair as Pair3, map_constructor as map_constructor66, generic_eq as generic_eq72, list_get as list_get11, string_from_code_point as string_from_code_point61, string_get as string_get36, string_next as string_next38, int_add as int_add7, int_to_string as int_to_string6, str_cat as str_cat9
from temper_core.regex import regex_compile_formatted as regex_compile_formatted67, regex_compiled_found as regex_compiled_found68, regex_compiled_find as regex_compiled_find69, regex_compiled_replace as regex_compiled_replace70, regex_compiled_split as regex_compiled_split71, regex_formatter_push_capture_name as regex_formatter_push_capture_name73, regex_formatter_push_code_to as regex_formatter_push_code_to74
pair_2598 = Pair3
map_constructor_2599 = map_constructor66
regex_compile_formatted_2600 = regex_compile_formatted67
regex_compiled_found_2601 = regex_compiled_found68
regex_compiled_find_2602 = regex_compiled_find69
regex_compiled_replace_2603 = regex_compiled_replace70
regex_compiled_split_2604 = regex_compiled_split71
generic_eq_2606 = generic_eq72
regex_formatter_push_capture_name_2608 = regex_formatter_push_capture_name73
list_get_2609 = list_get11
string_from_code_point_2610 = string_from_code_point61
regex_formatter_push_code_to_2611 = regex_formatter_push_code_to74
string_get_2613 = string_get36
string_next_2614 = string_next38
len_2615 = len5
int_add_2616 = int_add7
int_to_string_2618 = int_to_string6
str_cat_2619 = str_cat9
list_2621 = list2
tuple_2623 = tuple0
class RegexNode(metaclass = ABCMeta48):
    def compiled(this_42) -> 'Regex':
        return Regex(this_42)
    def found(this_43, text_170: 'str14') -> 'bool12':
        return this_43.compiled().found(text_170)
    def find(this_44, text_173: 'str14') -> 'Match':
        return this_44.compiled().find(text_173)
    def replace(this_45, text_176: 'str14', format_177: 'Callable15[[Match], str14]') -> 'str14':
        'Replace and split functions are also available. Both apply to all matches in\nthe string, replacing all or splitting at all.\n\nthis__45: RegexNode\n\ntext__176: String\n\nformat__177: fn (Match): String\n'
        return this_45.compiled().replace(text_176, format_177)
    def split(this_46, text_180: 'str14') -> 'Sequence16[str14]':
        return this_46.compiled().split(text_180)
class Capture(RegexNode):
    '`Capture` is a [group](#groups) that remembers the matched text for later\naccess. Temper supports only named matches, with current intended syntax\n`/(?name = ...)/`.'
    name_182: 'str14'
    item_183: 'RegexNode'
    __slots__ = ('name_182', 'item_183')
    def __init__(this_87, name_185: 'str14', item_186: 'RegexNode') -> None:
        this_87.name_182 = name_185
        this_87.item_183 = item_186
    @property
    def name(this_437) -> 'str14':
        return this_437.name_182
    @property
    def item(this_440) -> 'RegexNode':
        return this_440.item_183
class CodePart(RegexNode, metaclass = ABCMeta48):
    pass
class CodePoints(CodePart):
    value_187: 'str14'
    __slots__ = ('value_187',)
    def __init__(this_89, value_189: 'str14') -> None:
        this_89.value_187 = value_189
    @property
    def value(this_443) -> 'str14':
        return this_443.value_187
class Special(RegexNode, metaclass = ABCMeta48):
    pass
class SpecialSet(CodePart, Special, metaclass = ABCMeta48):
    pass
class CodeRange(CodePart):
    min_197: 'int19'
    max_198: 'int19'
    __slots__ = ('min_197', 'max_198')
    def __init__(this_105, min_200: 'int19', max_201: 'int19') -> None:
        this_105.min_197 = min_200
        this_105.max_198 = max_201
    @property
    def min(this_446) -> 'int19':
        return this_446.min_197
    @property
    def max(this_449) -> 'int19':
        return this_449.max_198
class CodeSet(RegexNode):
    items_202: 'Sequence16[CodePart]'
    negated_203: 'bool12'
    __slots__ = ('items_202', 'negated_203')
    def __init__(this_107, items_205: 'Sequence16[CodePart]', negated_535: 'Union17[bool12, None]' = None) -> None:
        _negated_535: 'Union17[bool12, None]' = negated_535
        negated_206: 'bool12'
        if _negated_535 is None:
            negated_206 = False
        else:
            negated_206 = _negated_535
        this_107.items_202 = items_205
        this_107.negated_203 = negated_206
    @property
    def items(this_452) -> 'Sequence16[CodePart]':
        return this_452.items_202
    @property
    def negated(this_455) -> 'bool12':
        return this_455.negated_203
class Or(RegexNode):
    '`Or` matches any one of multiple options, such as `/ab|cd|e*/`.'
    items_207: 'Sequence16[RegexNode]'
    __slots__ = ('items_207',)
    def __init__(this_110, items_209: 'Sequence16[RegexNode]') -> None:
        this_110.items_207 = items_209
    @property
    def items(this_458) -> 'Sequence16[RegexNode]':
        return this_458.items_207
class Repeat(RegexNode):
    item_210: 'RegexNode'
    min_211: 'int19'
    max_212: 'Union17[int19, None]'
    reluctant_213: 'bool12'
    __slots__ = ('item_210', 'min_211', 'max_212', 'reluctant_213')
    def __init__(this_113, item_215: 'RegexNode', min_216: 'int19', max_217: 'Union17[int19, None]', reluctant_537: 'Union17[bool12, None]' = None) -> None:
        _reluctant_537: 'Union17[bool12, None]' = reluctant_537
        reluctant_218: 'bool12'
        if _reluctant_537 is None:
            reluctant_218 = False
        else:
            reluctant_218 = _reluctant_537
        this_113.item_210 = item_215
        this_113.min_211 = min_216
        this_113.max_212 = max_217
        this_113.reluctant_213 = reluctant_218
    @property
    def item(this_461) -> 'RegexNode':
        return this_461.item_210
    @property
    def min(this_464) -> 'int19':
        return this_464.min_211
    @property
    def max(this_467) -> 'Union17[int19, None]':
        return this_467.max_212
    @property
    def reluctant(this_470) -> 'bool12':
        return this_470.reluctant_213
class Sequence(RegexNode):
    '`Sequence` strings along multiple other regexes in order.'
    items_227: 'Sequence16[RegexNode]'
    __slots__ = ('items_227',)
    def __init__(this_119, items_229: 'Sequence16[RegexNode]') -> None:
        this_119.items_227 = items_229
    @property
    def items(this_473) -> 'Sequence16[RegexNode]':
        return this_473.items_227
class Match:
    full_230: 'Group'
    groups_231: 'MappingProxyType53[str14, Group]'
    __slots__ = ('full_230', 'groups_231')
    def __init__(this_122, full_233: 'Group', groups_234: 'MappingProxyType53[str14, Group]') -> None:
        this_122.full_230 = full_233
        this_122.groups_231 = groups_234
    @property
    def full(this_488) -> 'Group':
        return this_488.full_230
    @property
    def groups(this_491) -> 'MappingProxyType53[str14, Group]':
        return this_491.groups_231
class Group:
    name_235: 'str14'
    value_236: 'str14'
    begin_237: 'int19'
    end_238: 'int19'
    __slots__ = ('name_235', 'value_236', 'begin_237', 'end_238')
    def __init__(this_125, name_240: 'str14', value_241: 'str14', begin_242: 'int19', end_243: 'int19') -> None:
        this_125.name_235 = name_240
        this_125.value_236 = value_241
        this_125.begin_237 = begin_242
        this_125.end_238 = end_243
    @property
    def name(this_476) -> 'str14':
        return this_476.name_235
    @property
    def value(this_479) -> 'str14':
        return this_479.value_236
    @property
    def begin(this_482) -> 'int19':
        return this_482.begin_237
    @property
    def end(this_485) -> 'int19':
        return this_485.end_238
class RegexRefs_54:
    code_points_244: 'CodePoints'
    group_245: 'Group'
    match_246: 'Match'
    or_object_247: 'Or'
    __slots__ = ('code_points_244', 'group_245', 'match_246', 'or_object_247')
    def __init__(this_127, code_points_539: 'Union17[CodePoints, None]' = None, group_541: 'Union17[Group, None]' = None, match_543: 'Union17[Match, None]' = None, or_object_545: 'Union17[Or, None]' = None) -> None:
        _code_points_539: 'Union17[CodePoints, None]' = code_points_539
        _group_541: 'Union17[Group, None]' = group_541
        _match_543: 'Union17[Match, None]' = match_543
        _or_object_545: 'Union17[Or, None]' = or_object_545
        t_1259: 'CodePoints'
        t_1260: 'Group'
        t_1262: 'MappingProxyType53[str14, Group]'
        t_1263: 'Match'
        t_1264: 'Or'
        code_points_249: 'CodePoints'
        if _code_points_539 is None:
            t_1259 = CodePoints('')
            code_points_249 = t_1259
        else:
            code_points_249 = _code_points_539
        group_250: 'Group'
        if _group_541 is None:
            t_1260 = Group('', '', 0, 0)
            group_250 = t_1260
        else:
            group_250 = _group_541
        match_251: 'Match'
        if _match_543 is None:
            t_1262 = map_constructor_2599((pair_2598('', group_250),))
            t_1263 = Match(group_250, t_1262)
            match_251 = t_1263
        else:
            match_251 = _match_543
        or_object_252: 'Or'
        if _or_object_545 is None:
            t_1264 = Or(())
            or_object_252 = t_1264
        else:
            or_object_252 = _or_object_545
        this_127.code_points_244 = code_points_249
        this_127.group_245 = group_250
        this_127.match_246 = match_251
        this_127.or_object_247 = or_object_252
    @property
    def code_points(this_494) -> 'CodePoints':
        return this_494.code_points_244
    @property
    def group(this_497) -> 'Group':
        return this_497.group_245
    @property
    def match_(this_500) -> 'Match':
        return this_500.match_246
    @property
    def or_object(this_503) -> 'Or':
        return this_503.or_object_247
class Regex:
    data_253: 'RegexNode'
    compiled_272: 'Any58'
    __slots__ = ('data_253', 'compiled_272')
    def __init__(this_55, data_255: 'RegexNode') -> None:
        t_412: 'RegexNode' = data_255
        this_55.data_253 = t_412
        formatted_257: 'str14' = RegexFormatter_64.regex_format(data_255)
        t_1143: 'Any58' = regex_compile_formatted_2600(data_255, formatted_257)
        this_55.compiled_272 = t_1143
    def found(this_56, text_259: 'str14') -> 'bool12':
        return regex_compiled_found_2601(this_56, this_56.compiled_272, text_259)
    def find(this_57, text_262: 'str14', begin_547: 'Union17[int19, None]' = None) -> 'Match':
        _begin_547: 'Union17[int19, None]' = begin_547
        begin_263: 'int19'
        if _begin_547 is None:
            begin_263 = 0
        else:
            begin_263 = _begin_547
        return regex_compiled_find_2602(this_57, this_57.compiled_272, text_262, begin_263, regex_refs_162)
    def replace(this_58, text_266: 'str14', format_267: 'Callable15[[Match], str14]') -> 'str14':
        return regex_compiled_replace_2603(this_58, this_58.compiled_272, text_266, format_267, regex_refs_162)
    def split(this_59, text_270: 'str14') -> 'Sequence16[str14]':
        return regex_compiled_split_2604(this_59, this_59.compiled_272, text_270, regex_refs_162)
    @property
    def data(this_530) -> 'RegexNode':
        return this_530.data_253
class RegexFormatter_64:
    out_294: 'list2[str14]'
    __slots__ = ('out_294',)
    @staticmethod
    def regex_format(data_300: 'RegexNode') -> 'str14':
        return RegexFormatter_64().format(data_300)
    def format(this_65, regex_303: 'RegexNode') -> 'str14':
        this_65.push_regex_305(regex_303)
        return ''.join(this_65.out_294)
    def push_regex_305(this_66, regex_306: 'RegexNode') -> 'None':
        t_868: 'Capture'
        t_869: 'CodePoints'
        t_870: 'CodeRange'
        t_871: 'CodeSet'
        t_872: 'Or'
        t_873: 'Repeat'
        t_874: 'Sequence'
        if isinstance56(regex_306, Capture):
            t_868 = cast_by_type57(regex_306, Capture)
            this_66.push_capture_308(t_868)
        elif isinstance56(regex_306, CodePoints):
            t_869 = cast_by_type57(regex_306, CodePoints)
            this_66.push_code_points_326(t_869, False)
        elif isinstance56(regex_306, CodeRange):
            t_870 = cast_by_type57(regex_306, CodeRange)
            this_66.push_code_range_332(t_870)
        elif isinstance56(regex_306, CodeSet):
            t_871 = cast_by_type57(regex_306, CodeSet)
            this_66.push_code_set_338(t_871)
        elif isinstance56(regex_306, Or):
            t_872 = cast_by_type57(regex_306, Or)
            this_66.push_or_350(t_872)
        elif isinstance56(regex_306, Repeat):
            t_873 = cast_by_type57(regex_306, Repeat)
            this_66.push_repeat_354(t_873)
        elif isinstance56(regex_306, Sequence):
            t_874 = cast_by_type57(regex_306, Sequence)
            this_66.push_sequence_359(t_874)
        elif generic_eq_2606(regex_306, begin):
            this_66.out_294.append('^')
        elif generic_eq_2606(regex_306, dot):
            this_66.out_294.append('.')
        elif generic_eq_2606(regex_306, end):
            this_66.out_294.append('$')
        elif generic_eq_2606(regex_306, word_boundary):
            this_66.out_294.append('\\b')
        elif generic_eq_2606(regex_306, digit):
            this_66.out_294.append('\\d')
        elif generic_eq_2606(regex_306, space):
            this_66.out_294.append('\\s')
        elif generic_eq_2606(regex_306, word):
            this_66.out_294.append('\\w')
    def push_capture_308(this_67, capture_309: 'Capture') -> 'None':
        this_67.out_294.append('(')
        t_842: 'list2[str14]' = this_67.out_294
        t_1229: 'str14' = capture_309.name
        regex_formatter_push_capture_name_2608(this_67, t_842, t_1229)
        t_1231: 'RegexNode' = capture_309.item
        this_67.push_regex_305(t_1231)
        this_67.out_294.append(')')
    def push_code_315(this_69, code_316: 'int19', inside_code_set_317: 'bool12') -> 'None':
        t_830: 'bool12'
        t_831: 'bool12'
        t_832: 'str14'
        t_834: 'str14'
        t_835: 'bool12'
        t_836: 'bool12'
        t_837: 'bool12'
        t_838: 'bool12'
        t_839: 'str14'
        with Label55() as fn_318:
            special_escape_319: 'str14'
            if code_316 == Codes_81.carriage_return:
                special_escape_319 = 'r'
            elif code_316 == Codes_81.newline:
                special_escape_319 = 'n'
            elif code_316 == Codes_81.tab:
                special_escape_319 = 't'
            else:
                special_escape_319 = ''
            if special_escape_319 != '':
                this_69.out_294.append('\\')
                this_69.out_294.append(special_escape_319)
                fn_318.break_()
            if code_316 <= 127:
                escape_need_320: 'int19' = list_get_2609(escape_needs_163, code_316)
                if escape_need_320 == 2:
                    t_831 = True
                else:
                    if inside_code_set_317:
                        t_830 = code_316 == Codes_81.dash
                    else:
                        t_830 = False
                    t_831 = t_830
                if t_831:
                    this_69.out_294.append('\\')
                    t_832 = string_from_code_point_2610(code_316)
                    this_69.out_294.append(t_832)
                    fn_318.break_()
                elif escape_need_320 == 0:
                    t_834 = string_from_code_point_2610(code_316)
                    this_69.out_294.append(t_834)
                    fn_318.break_()
            if code_316 >= Codes_81.supplemental_min:
                t_838 = True
            else:
                if code_316 > Codes_81.high_control_max:
                    if Codes_81.surrogate_min <= code_316:
                        t_835 = code_316 <= Codes_81.surrogate_max
                    else:
                        t_835 = False
                    if t_835:
                        t_836 = True
                    else:
                        t_836 = code_316 == Codes_81.uint16_max
                    t_837 = not t_836
                else:
                    t_837 = False
                t_838 = t_837
            if t_838:
                t_839 = string_from_code_point_2610(code_316)
                this_69.out_294.append(t_839)
            else:
                regex_formatter_push_code_to_2611(this_69, this_69.out_294, code_316, inside_code_set_317)
    def push_code_points_326(this_71, code_points_327: 'CodePoints', inside_code_set_328: 'bool12') -> 'None':
        t_1216: 'int19'
        t_1218: 'int19'
        value_330: 'str14' = code_points_327.value
        index_331: 'int19' = 0
        while True:
            if not len5(value_330) > index_331:
                break
            t_1216 = string_get_2613(value_330, index_331)
            this_71.push_code_315(t_1216, inside_code_set_328)
            t_1218 = string_next_2614(value_330, index_331)
            index_331 = t_1218
    def push_code_range_332(this_72, code_range_333: 'CodeRange') -> 'None':
        this_72.out_294.append('[')
        this_72.push_code_range_unwrapped_335(code_range_333)
        this_72.out_294.append(']')
    def push_code_range_unwrapped_335(this_73, code_range_336: 'CodeRange') -> 'None':
        t_1206: 'int19' = code_range_336.min
        this_73.push_code_315(t_1206, True)
        this_73.out_294.append('-')
        t_1209: 'int19' = code_range_336.max
        this_73.push_code_315(t_1209, True)
    def push_code_set_338(this_74, code_set_339: 'CodeSet') -> 'None':
        t_1200: 'int19'
        t_1202: 'CodePart'
        t_815: 'CodeSet'
        adjusted_341: 'RegexNode' = this_74.adjust_code_set_343(code_set_339, regex_refs_162)
        if isinstance56(adjusted_341, CodeSet):
            t_815 = cast_by_type57(adjusted_341, CodeSet)
            this_74.out_294.append('[')
            if t_815.negated:
                this_74.out_294.append('^')
            i_342: 'int19' = 0
            while True:
                t_1200 = len_2615(t_815.items)
                if not i_342 < t_1200:
                    break
                t_1202 = list_get_2609(t_815.items, i_342)
                this_74.push_code_set_item_347(t_1202)
                i_342 = int_add_2616(i_342, 1)
            this_74.out_294.append(']')
        else:
            this_74.push_regex_305(adjusted_341)
    def adjust_code_set_343(this_75, code_set_344: 'CodeSet', regex_refs_345: 'RegexRefs_54') -> 'RegexNode':
        return code_set_344
    def push_code_set_item_347(this_76, code_part_348: 'CodePart') -> 'None':
        t_803: 'CodePoints'
        t_804: 'CodeRange'
        t_805: 'SpecialSet'
        if isinstance56(code_part_348, CodePoints):
            t_803 = cast_by_type57(code_part_348, CodePoints)
            this_76.push_code_points_326(t_803, True)
        elif isinstance56(code_part_348, CodeRange):
            t_804 = cast_by_type57(code_part_348, CodeRange)
            this_76.push_code_range_unwrapped_335(t_804)
        elif isinstance56(code_part_348, SpecialSet):
            t_805 = cast_by_type57(code_part_348, SpecialSet)
            this_76.push_regex_305(t_805)
    def push_or_350(this_77, or_351: 'Or') -> 'None':
        t_1179: 'RegexNode'
        t_1182: 'int19'
        t_1185: 'RegexNode'
        if not (not or_351.items):
            this_77.out_294.append('(?:')
            t_1179 = list_get_2609(or_351.items, 0)
            this_77.push_regex_305(t_1179)
            i_353: 'int19' = 1
            while True:
                t_1182 = len_2615(or_351.items)
                if not i_353 < t_1182:
                    break
                this_77.out_294.append('|')
                t_1185 = list_get_2609(or_351.items, i_353)
                this_77.push_regex_305(t_1185)
                i_353 = int_add_2616(i_353, 1)
            this_77.out_294.append(')')
    def push_repeat_354(this_78, repeat_355: 'Repeat') -> 'None':
        t_1167: 'str14'
        t_1170: 'str14'
        t_780: 'bool12'
        t_781: 'bool12'
        t_782: 'bool12'
        this_78.out_294.append('(?:')
        t_1159: 'RegexNode' = repeat_355.item
        this_78.push_regex_305(t_1159)
        this_78.out_294.append(')')
        min_357: 'int19' = repeat_355.min
        max_358: 'Union17[int19, None]' = repeat_355.max
        if min_357 == 0:
            t_780 = max_358 == 1
        else:
            t_780 = False
        if t_780:
            this_78.out_294.append('?')
        else:
            if min_357 == 0:
                t_781 = max_358 is None
            else:
                t_781 = False
            if t_781:
                this_78.out_294.append('*')
            else:
                if min_357 == 1:
                    t_782 = max_358 is None
                else:
                    t_782 = False
                if t_782:
                    this_78.out_294.append('+')
                else:
                    t_1167 = int_to_string_2618(min_357)
                    this_78.out_294.append(str_cat_2619('{', t_1167))
                    if min_357 != max_358:
                        this_78.out_294.append(',')
                        if not max_358 is None:
                            t_1170 = int_to_string_2618(max_358)
                            this_78.out_294.append(t_1170)
                    this_78.out_294.append('}')
        if repeat_355.reluctant:
            this_78.out_294.append('?')
    def push_sequence_359(this_79, sequence_360: 'Sequence') -> 'None':
        t_1154: 'int19'
        t_1156: 'RegexNode'
        i_362: 'int19' = 0
        while True:
            t_1154 = len_2615(sequence_360.items)
            if not i_362 < t_1154:
                break
            t_1156 = list_get_2609(sequence_360.items, i_362)
            this_79.push_regex_305(t_1156)
            i_362 = int_add_2616(i_362, 1)
    def max_code(this_80, code_part_364: 'CodePart') -> 'Union17[int19, None]':
        return_157: 'Union17[int19, None]'
        t_1150: 'int19'
        t_768: 'CodePoints'
        if isinstance56(code_part_364, CodePoints):
            t_768 = cast_by_type57(code_part_364, CodePoints)
            value_366: 'str14' = t_768.value
            if not value_366:
                return_157 = None
            else:
                max_367: 'int19' = 0
                index_368: 'int19' = 0
                while True:
                    if not len5(value_366) > index_368:
                        break
                    next_369: 'int19' = string_get_2613(value_366, index_368)
                    if next_369 > max_367:
                        max_367 = next_369
                    t_1150 = string_next_2614(value_366, index_368)
                    index_368 = t_1150
                return_157 = max_367
        elif isinstance56(code_part_364, CodeRange):
            return_157 = cast_by_type57(code_part_364, CodeRange).max
        elif generic_eq_2606(code_part_364, digit):
            return_157 = Codes_81.digit9
        elif generic_eq_2606(code_part_364, space):
            return_157 = Codes_81.space
        elif generic_eq_2606(code_part_364, word):
            return_157 = Codes_81.lower_z
        else:
            return_157 = None
        return return_157
    def __init__(this_138) -> None:
        t_1144: 'list2[str14]' = ['']
        this_138.out_294 = t_1144
class Codes_81:
    ampersand: ClassVar50['int19']
    backslash: ClassVar50['int19']
    caret: ClassVar50['int19']
    carriage_return: ClassVar50['int19']
    curly_left: ClassVar50['int19']
    curly_right: ClassVar50['int19']
    dash: ClassVar50['int19']
    dot: ClassVar50['int19']
    high_control_min: ClassVar50['int19']
    high_control_max: ClassVar50['int19']
    digit0: ClassVar50['int19']
    digit9: ClassVar50['int19']
    lower_a: ClassVar50['int19']
    lower_z: ClassVar50['int19']
    newline: ClassVar50['int19']
    peso: ClassVar50['int19']
    pipe: ClassVar50['int19']
    plus: ClassVar50['int19']
    question: ClassVar50['int19']
    round_left: ClassVar50['int19']
    round_right: ClassVar50['int19']
    slash: ClassVar50['int19']
    square_left: ClassVar50['int19']
    square_right: ClassVar50['int19']
    star: ClassVar50['int19']
    tab: ClassVar50['int19']
    tilde: ClassVar50['int19']
    upper_a: ClassVar50['int19']
    upper_z: ClassVar50['int19']
    space: ClassVar50['int19']
    surrogate_min: ClassVar50['int19']
    surrogate_max: ClassVar50['int19']
    supplemental_min: ClassVar50['int19']
    uint16_max: ClassVar50['int19']
    underscore: ClassVar50['int19']
    __slots__ = ()
    def __init__(this_159) -> None:
        pass
Codes_81.ampersand = 38
Codes_81.backslash = 92
Codes_81.caret = 94
Codes_81.carriage_return = 13
Codes_81.curly_left = 123
Codes_81.curly_right = 125
Codes_81.dash = 45
Codes_81.dot = 46
Codes_81.high_control_min = 127
Codes_81.high_control_max = 159
Codes_81.digit0 = 48
Codes_81.digit9 = 57
Codes_81.lower_a = 97
Codes_81.lower_z = 122
Codes_81.newline = 10
Codes_81.peso = 36
Codes_81.pipe = 124
Codes_81.plus = 43
Codes_81.question = 63
Codes_81.round_left = 40
Codes_81.round_right = 41
Codes_81.slash = 47
Codes_81.square_left = 91
Codes_81.square_right = 93
Codes_81.star = 42
Codes_81.tab = 9
Codes_81.tilde = 42
Codes_81.upper_a = 65
Codes_81.upper_z = 90
Codes_81.space = 32
Codes_81.surrogate_min = 55296
Codes_81.surrogate_max = 57343
Codes_81.supplemental_min = 65536
Codes_81.uint16_max = 65535
Codes_81.underscore = 95
class Begin_47(Special):
    __slots__ = ()
    def __init__(this_91) -> None:
        pass
begin: 'Special' = Begin_47()
class Dot_48(Special):
    __slots__ = ()
    def __init__(this_93) -> None:
        pass
dot: 'Special' = Dot_48()
class End_49(Special):
    __slots__ = ()
    def __init__(this_95) -> None:
        pass
end: 'Special' = End_49()
class WordBoundary_50(Special):
    __slots__ = ()
    def __init__(this_97) -> None:
        pass
word_boundary: 'Special' = WordBoundary_50()
class Digit_51(SpecialSet):
    __slots__ = ()
    def __init__(this_99) -> None:
        pass
digit: 'SpecialSet' = Digit_51()
class Space_52(SpecialSet):
    __slots__ = ()
    def __init__(this_101) -> None:
        pass
space: 'SpecialSet' = Space_52()
class Word_53(SpecialSet):
    __slots__ = ()
    def __init__(this_103) -> None:
        pass
word: 'SpecialSet' = Word_53()
def build_escape_needs_161() -> 'Sequence16[int19]':
    t_907: 'bool12'
    t_908: 'bool12'
    t_909: 'bool12'
    t_910: 'bool12'
    t_911: 'bool12'
    t_912: 'bool12'
    t_913: 'bool12'
    t_914: 'bool12'
    t_915: 'bool12'
    t_916: 'bool12'
    t_917: 'bool12'
    t_918: 'bool12'
    t_919: 'bool12'
    t_920: 'bool12'
    t_921: 'bool12'
    t_922: 'bool12'
    t_923: 'bool12'
    t_924: 'bool12'
    t_925: 'bool12'
    t_926: 'bool12'
    t_927: 'bool12'
    t_928: 'bool12'
    t_929: 'bool12'
    t_930: 'bool12'
    t_931: 'int19'
    escape_needs_372: 'MutableSequence13[int19]' = list_2621()
    code_373: 'int19' = 0
    while code_373 < 127:
        if code_373 == Codes_81.dash:
            t_914 = True
        else:
            if code_373 == Codes_81.space:
                t_913 = True
            else:
                if code_373 == Codes_81.underscore:
                    t_912 = True
                else:
                    if Codes_81.digit0 <= code_373:
                        t_907 = code_373 <= Codes_81.digit9
                    else:
                        t_907 = False
                    if t_907:
                        t_911 = True
                    else:
                        if Codes_81.upper_a <= code_373:
                            t_908 = code_373 <= Codes_81.upper_z
                        else:
                            t_908 = False
                        if t_908:
                            t_910 = True
                        else:
                            if Codes_81.lower_a <= code_373:
                                t_909 = code_373 <= Codes_81.lower_z
                            else:
                                t_909 = False
                            t_910 = t_909
                        t_911 = t_910
                    t_912 = t_911
                t_913 = t_912
            t_914 = t_913
        if t_914:
            t_931 = 0
        else:
            if code_373 == Codes_81.ampersand:
                t_930 = True
            else:
                if code_373 == Codes_81.backslash:
                    t_929 = True
                else:
                    if code_373 == Codes_81.caret:
                        t_928 = True
                    else:
                        if code_373 == Codes_81.curly_left:
                            t_927 = True
                        else:
                            if code_373 == Codes_81.curly_right:
                                t_926 = True
                            else:
                                if code_373 == Codes_81.dot:
                                    t_925 = True
                                else:
                                    if code_373 == Codes_81.peso:
                                        t_924 = True
                                    else:
                                        if code_373 == Codes_81.pipe:
                                            t_923 = True
                                        else:
                                            if code_373 == Codes_81.plus:
                                                t_922 = True
                                            else:
                                                if code_373 == Codes_81.question:
                                                    t_921 = True
                                                else:
                                                    if code_373 == Codes_81.round_left:
                                                        t_920 = True
                                                    else:
                                                        if code_373 == Codes_81.round_right:
                                                            t_919 = True
                                                        else:
                                                            if code_373 == Codes_81.slash:
                                                                t_918 = True
                                                            else:
                                                                if code_373 == Codes_81.square_left:
                                                                    t_917 = True
                                                                else:
                                                                    if code_373 == Codes_81.square_right:
                                                                        t_916 = True
                                                                    else:
                                                                        if code_373 == Codes_81.star:
                                                                            t_915 = True
                                                                        else:
                                                                            t_915 = code_373 == Codes_81.tilde
                                                                        t_916 = t_915
                                                                    t_917 = t_916
                                                                t_918 = t_917
                                                            t_919 = t_918
                                                        t_920 = t_919
                                                    t_921 = t_920
                                                t_922 = t_921
                                            t_923 = t_922
                                        t_924 = t_923
                                    t_925 = t_924
                                t_926 = t_925
                            t_927 = t_926
                        t_928 = t_927
                    t_929 = t_928
                t_930 = t_929
            if t_930:
                t_931 = 2
            else:
                t_931 = 1
        escape_needs_372.append(t_931)
        code_373 = int_add_2616(code_373, 1)
    return tuple_2623(escape_needs_372)
escape_needs_163: 'Sequence16[int19]' = build_escape_needs_161()
regex_refs_162: 'RegexRefs_54' = RegexRefs_54()
def entire(item_219: 'RegexNode') -> 'RegexNode':
    return Sequence((begin, item_219, end))
def one_or_more(item_221: 'RegexNode', reluctant_549: 'Union17[bool12, None]' = None) -> 'Repeat':
    _reluctant_549: 'Union17[bool12, None]' = reluctant_549
    reluctant_222: 'bool12'
    if _reluctant_549 is None:
        reluctant_222 = False
    else:
        reluctant_222 = _reluctant_549
    return Repeat(item_221, 1, None, reluctant_222)
def optional(item_224: 'RegexNode', reluctant_551: 'Union17[bool12, None]' = None) -> 'Repeat':
    _reluctant_551: 'Union17[bool12, None]' = reluctant_551
    reluctant_225: 'bool12'
    if _reluctant_551 is None:
        reluctant_225 = False
    else:
        reluctant_225 = _reluctant_551
    return Repeat(item_224, 0, 1, reluctant_225)
