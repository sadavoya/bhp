def sum(number_one, number_two):
    num_one_int = convert_integer(number_one)
    num_two_int = convert_integer(number_two)

    result = num_one_int + num_two_int
    return result
def convert_integer(number_string):
    converted_integer = int(number_string)
    return converted_integer
answer = sum("1", "2")
