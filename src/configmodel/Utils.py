# -*- coding: utf-8 -*-


def pascal_case_to_snake_case(pascal_case_string):
    """
    Convert PascalCase string to snake_case string
    """
    snake_case_string = ""
    for index, char in enumerate(pascal_case_string):
        if index == 0:
            snake_case_string += char.lower()
        else:
            if char.isupper():
                snake_case_string += "_%s" % char.lower()
            else:
                snake_case_string += char
    return snake_case_string
