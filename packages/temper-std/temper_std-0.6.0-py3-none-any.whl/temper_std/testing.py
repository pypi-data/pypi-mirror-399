from builtins import bool as bool12, str as str14, Exception as Exception18, int as int19, list as list2, tuple as tuple0, len as len5
from typing import MutableSequence as MutableSequence13, Callable as Callable15, Sequence as Sequence16, Union as Union17
from temper_core import Pair as Pair3, list_join as list_join1, list_map as list_map4, int_to_string as int_to_string6, int_add as int_add7, listed_reduce_from as listed_reduce_from8, str_cat as str_cat9, string_split as string_split10, list_get as list_get11
tuple_2526 = tuple0
list_join_2528 = list_join1
list_2529 = list2
pair_2530 = Pair3
list_map_2531 = list_map4
len_2532 = len5
int_to_string_2533 = int_to_string6
int_add_2534 = int_add7
listed_reduce_from_2535 = listed_reduce_from8
str_cat_2536 = str_cat9
string_split_2537 = string_split10
list_get_2538 = list_get11
class Test:
    failed_on_assert_60: 'bool12'
    passing_61: 'bool12'
    messages_62: 'MutableSequence13[str14]'
    __slots__ = ('failed_on_assert_60', 'passing_61', 'messages_62')
    def assert_(this_9, success_38: 'bool12', message_39: 'Callable15[[], str14]') -> 'None':
        t_353: 'str14'
        if not success_38:
            this_9.passing_61 = False
            t_353 = message_39()
            this_9.messages_62.append(t_353)
    def assert_hard(this_10, success_42: 'bool12', message_43: 'Callable15[[], str14]') -> 'None':
        this_10.assert_(success_42, message_43)
        if not success_42:
            this_10.failed_on_assert_60 = True
            assert False, str14(this_10.messages_combined())
    def soft_fail_to_hard(this_11) -> 'None':
        if this_11.has_unhandled_fail:
            this_11.failed_on_assert_60 = True
            assert False, str14(this_11.messages_combined())
    @property
    def passing(this_13) -> 'bool12':
        return this_13.passing_61
    def messages(this_14) -> 'Sequence16[str14]':
        "Messages access is presented as a function because it likely allocates. Also,\nmessages might be automatically constructed in some cases, so it's possibly\nunwise to depend on their exact formatting.\n\nthis__14: Test\n"
        return tuple_2526(this_14.messages_62)
    @property
    def failed_on_assert(this_15) -> 'bool12':
        return this_15.failed_on_assert_60
    @property
    def has_unhandled_fail(this_16) -> 'bool12':
        t_224: 'bool12'
        if this_16.failed_on_assert_60:
            t_224 = True
        else:
            t_224 = this_16.passing_61
        return not t_224
    def messages_combined(this_17) -> 'Union17[str14, None]':
        return_31: 'Union17[str14, None]'
        if not this_17.messages_62:
            return_31 = None
        else:
            def fn_346(it_59: 'str14') -> 'str14':
                return it_59
            return_31 = list_join_2528(this_17.messages_62, ', ', fn_346)
        return return_31
    def __init__(this_21) -> None:
        this_21.failed_on_assert_60 = False
        this_21.passing_61 = True
        t_345: 'MutableSequence13[str14]' = list_2529()
        this_21.messages_62 = t_345
def process_test_cases(test_cases_64: 'Sequence16[(Pair3[str14, (Callable15[[Test], None])])]') -> 'Sequence16[(Pair3[str14, (Sequence16[str14])])]':
    def fn_342(test_case_66: 'Pair3[str14, (Callable15[[Test], None])]') -> 'Pair3[str14, (Sequence16[str14])]':
        t_337: 'bool12'
        t_340: 'Sequence16[str14]'
        t_206: 'bool12'
        t_208: 'bool12'
        key_68: 'str14' = test_case_66.key
        fun_69: 'Callable15[[Test], None]' = test_case_66.value
        test_70: 'Test' = Test()
        had_bubble_71: 'bool12' = False
        try:
            fun_69(test_70)
        except Exception18:
            had_bubble_71 = True
        messages_72: 'Sequence16[str14]' = test_70.messages()
        failures_73: 'Sequence16[str14]'
        if test_70.passing:
            t_206 = not had_bubble_71
        else:
            t_206 = False
        if t_206:
            failures_73 = ()
        else:
            if had_bubble_71:
                t_337 = test_70.failed_on_assert
                t_208 = not t_337
            else:
                t_208 = False
            if t_208:
                all_messages_74: 'MutableSequence13[str14]' = list_2529(messages_72)
                all_messages_74.append('Bubble')
                t_340 = tuple_2526(all_messages_74)
                failures_73 = t_340
            else:
                failures_73 = messages_72
        return pair_2530(key_68, failures_73)
    return list_map_2531(test_cases_64, fn_342)
def report_test_results(test_results_75: 'Sequence16[(Pair3[str14, (Sequence16[str14])])]', write_line_76: 'Callable15[[str14], None]') -> 'None':
    t_317: 'int19'
    write_line_76('<testsuites>')
    total_79: 'str14' = int_to_string_2533(len_2532(test_results_75))
    def fn_309(fails_81: 'int19', test_result_82: 'Pair3[str14, (Sequence16[str14])]') -> 'int19':
        t_180: 'int19'
        if not test_result_82.value:
            t_180 = 0
        else:
            t_180 = 1
        return int_add_2534(fails_81, t_180)
    fails_80: 'str14' = int_to_string_2533(listed_reduce_from_2535(test_results_75, 0, fn_309))
    totals_84: 'str14' = str_cat_2536("tests='", total_79, "' failures='", fails_80, "'")
    write_line_76(str_cat_2536("  <testsuite name='suite' ", totals_84, " time='0.0'>"))
    def escape_78(s_85: 'str14') -> 'str14':
        t_303: 'Sequence16[str14]' = string_split_2537(s_85, "'")
        def fn_302(x_87: 'str14') -> 'str14':
            return x_87
        return list_join_2528(t_303, '&apos;', fn_302)
    i_88: 'int19' = 0
    while True:
        t_317 = len_2532(test_results_75)
        if not i_88 < t_317:
            break
        test_result_89: 'Pair3[str14, (Sequence16[str14])]' = list_get_2538(test_results_75, i_88)
        failure_messages_90: 'Sequence16[str14]' = test_result_89.value
        name_91: 'str14' = escape_78(test_result_89.key)
        basics_92: 'str14' = str_cat_2536("name='", name_91, "' classname='", name_91, "' time='0.0'")
        if not failure_messages_90:
            write_line_76(str_cat_2536('    <testcase ', basics_92, ' />'))
        else:
            write_line_76(str_cat_2536('    <testcase ', basics_92, '>'))
            def fn_308(it_94: 'str14') -> 'str14':
                return it_94
            message_93: 'str14' = escape_78(list_join_2528(failure_messages_90, ', ', fn_308))
            write_line_76(str_cat_2536("      <failure message='", message_93, "' />"))
            write_line_76('    </testcase>')
        i_88 = int_add_2534(i_88, 1)
    write_line_76('  </testsuite>')
    write_line_76('</testsuites>')
def run_test_cases(test_cases_95: 'Sequence16[(Pair3[str14, (Callable15[[Test], None])])]') -> 'str14':
    report_97: 'list2[str14]' = ['']
    t_298: 'Sequence16[(Pair3[str14, (Sequence16[str14])])]' = process_test_cases(test_cases_95)
    def fn_296(line_98: 'str14') -> 'None':
        report_97.append(line_98)
        report_97.append('\n')
    report_test_results(t_298, fn_296)
    return ''.join(report_97)
def run_test(test_fun_99: 'Callable15[[Test], None]') -> 'None':
    test_101: 'Test' = Test()
    try:
        test_fun_99(test_101)
    except Exception18:
        def fn_290() -> 'str14':
            return 'bubble during test running'
        test_101.assert_(False, fn_290)
    test_101.soft_fail_to_hard()
