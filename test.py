a = '1万'
print(a.endswith('万'))
print(a[:-1])
print( int(a[:-1])*1000 if ''.endswith('万') else int(a))



