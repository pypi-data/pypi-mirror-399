

def camel_case_to_snake_case(camel_case_string):
    """
    Converts a camel case string to snake case.
    :param camel_case_string: String to convert to snake case.
    :return: String in snake case.
    """
    snake_case_chars = []
    for index, char in enumerate(camel_case_string):
        if char.isupper() and index != 0:
            snake_case_chars.append('_')
        snake_case_chars.append(char)
    return "".join(snake_case_chars).lower()


def snake_case_to_camel_case(snake_case_string):
    """
    Converts a snake case string to camel case.
    :param snake_case_string: String to convert to camel case.
    :return: String in camel case.
    """
    camel_case_chars = []
    for index, char in enumerate(snake_case_string):
        if char == '_':
            continue
        if index == 0 or snake_case_string[index - 1] == '_':
            camel_case_chars.append(char.upper())
        else:
            camel_case_chars.append(char)
    return "".join(camel_case_chars)
