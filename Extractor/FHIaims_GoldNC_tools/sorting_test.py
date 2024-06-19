data = [
    {'eval': 3, 'elem': [1, 2, 3, 4, 5]},
    {'eval': 2, 'elem': [2, 5, 1, 3, 7]},
    {'eval': 5, 'elem': [9, 2, 3, 4, 5]},
    {'eval': 1, 'elem': [9, 2, 3, 4, 5]},
    {'eval': 0, 'elem': [9, 2, 3, 4, 5]}
]
print(data)

sorted_data = sorted(data, key=lambda x: x['eval'])

print(sorted_data)
