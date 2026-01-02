from threading import Timer
from functools import reduce
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import operator
import jsonschema
import re
import random
import string
import inspect


def json_schema_validate(data: dict, schema: dict, index=""):
    """
    Validate an instance data under the given schema

    :param data: response json as dict
    :param schema: api json schema as dict
    :param index: input data index for trace used, example: userId
    """
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())

    errors = validator.iter_errors(data)
    schema_errors = ""
    for error in errors:
        schema_errors += f"\n{error.absolute_path}, {error.message}, {index}"
    if schema_errors:
        # raise jsonschema.ValidationError(schema_errors)
        raise AssertionError(schema_errors)


def find_column(sheet, index_row, find_str):
    for cell in sheet[str(index_row)]:
        if find_str == cell.value:
            return cell


def str_gen(char=string.ascii_letters + string.digits, size=20):
    return ''.join(random.choices(char, k=size))


def custom_round(number, digits=0):
    d = Decimal(str(number))
    factor = Decimal(f'1e{-digits}')
    return float(d.quantize(factor, rounding=ROUND_HALF_UP))


class RepeatingTimer(Timer):

    def __init__(self, interval, function, args=None, kwargs=None, recursion=False):
        """
        Call a function after a specified number of seconds till cancel:
        t = Timer(30.0, f, args=None, kwargs=None) t.start() t.cancel() # stop the timer's action if it's still waiting
        :param interval:
        :param function:
        :param args:
        :param kwargs:
        :param recursion: use function returned value to next call
        """
        super().__init__(interval, function, args=args, kwargs=kwargs)
        self.recursion = recursion

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            if self.recursion:
                func_result = self.function(*self.args, **self.kwargs)
                if isinstance(func_result, dict):
                    self.kwargs = func_result
                elif isinstance(func_result, list | tuple):
                    self.args = func_result
                else:
                    raise ValueError("in recursion=True, function must return dict, list or tuple")
            else:
                self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class DictTool:
    @staticmethod
    def transfer_json_path(path: str):
        """
        transfer json path to list
        :param path: json path, ex: "TRANRS[0].district[0].districtName"
        :return: list of json path , ex: ['TRANRS', 0, 'district', 0, 'districtName']
        """
        return [int(s) if s.isdigit() else s for s in re.split(r"\.", re.sub(r"\[(\d+)]", r".\g<1>", path))]

    @classmethod
    def get_by_path(cls, root: dict, items: list):
        """
        Access a nested object in root by item sequence.
        :param root: api request payload as dict format
        :param items: key path, ex: ['TRANRS', 0, 'district', 0, 'districtName']
        :return:
        """
        return reduce(operator.getitem, items, root)

    @classmethod
    def set_by_path(cls, root: dict, items: list, value):
        """
        Set a value in a nested object in root by item sequence.
        :param root: api request payload as dict format
        :param items: key path, ex: ['TRANRS', 0, 'district', 0, 'districtName']
        :param value: value of key that you want to set
        :return:
        """
        cls.get_by_path(root, items[:-1])[items[-1]] = value


def _find_project_root(possible_markers=None):
    if possible_markers is None:
        possible_markers = ["pyproject.toml", "setup.py", "requirements.txt", ".git"]

    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        for marker in possible_markers:
            if (parent / marker).exists():
                return parent
    # 如果都找不到，就回傳最上層資料夾
    return current_path.parents[-1]


_PROJECT_ROOT = _find_project_root()


def get_log_info(depth=1, project_root=_PROJECT_ROOT):
    """

    :param depth: counts of f_back in caller_frame.f_back
    :param project_root:
    :return: file_path, function_name, line_number
    """
    def repl(matchobj):
        if matchobj.group(0) == "\\":
            return ""
        else:
            return matchobj.group(0)[:-1] + "."

    caller_frame = inspect.currentframe()
    for i in range(depth):
        caller_frame = caller_frame.f_back
    # caller_frame = inspect.currentframe().f_back.f_back
    frame_info = inspect.getframeinfo(caller_frame)
    file_path = re.search(rf"{re.escape(str(project_root))}(.+)", frame_info.filename).group(1)
    function_name = frame_info.function
    line_number = frame_info.lineno

    matched_regex = ".*?\\\\"
    return re.sub(matched_regex, repl, file_path), function_name, line_number
