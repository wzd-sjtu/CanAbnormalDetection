

times = 0

'''
f = open('./src/origin.asc', 'r')
f1 = open('./src/{LoggingBlock1}.asc', 'w')
f2 = open('./src/{LoggingBlock2}.asc', 'w')
f3 = open('./src/{LoggingBlock3}.asc', 'w')
f4 = open('./src/{LoggingBlock4}.asc', 'w')

for line in f:
    if times >=0 and times <= 250000:
        f1.write(line)
    elif times > 250000 and times <= 500000:
        f2.write(line)
    elif times > 500000 and times <= 750000:
        f3.write(line)
    else:
        f4.write(line)

    times = times + 1
f.close()
f1.close()
f2.close()
f3.close()
f4.close()
'''
f = open('./src_of_real_data/target.csv', 'r')
f1 = open('./src_of_real_data/target1.csv', 'w')
f2 = open('./src_of_real_data/target2.csv', 'w')
f3 = open('./src_of_real_data/target3.csv', 'w')
f4 = open('./src_of_real_data/target4.csv', 'w')

state = 0
for line in f:
    if state == 0:
        f1.write(line)
        f2.write(line)
        f3.write(line)
        f4.write(line)
        state = 1
    else:
        if times >= 0 and times <= 250000:
            f1.write(line)
        elif times > 250000 and times <= 500000:
            f2.write(line)
        elif times > 500000 and times <= 750000:
            f3.write(line)
        else:
            f4.write(line)

    times = times + 1

f.close()
f1.close()
f2.close()
f3.close()
f4.close()
