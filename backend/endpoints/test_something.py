from typing import List

new_arr: list[object] = [{"name": "David"}]

print(new_arr)

# new_arr.append({"name": "Dean", "age": 13})

new_arr_2 = new_arr

new_arr_2.append({"name": "Dean", "age": 13})

print(new_arr_2)