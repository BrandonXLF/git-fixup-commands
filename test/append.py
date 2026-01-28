import sys

word = sys.argv[1]
filename = sys.argv[2]

with open(filename, 'a') as file:
	file.write(word + "\n")
