from subprocess import Popen, PIPE
import time


command = "python3"
levelcontrol = "5+5"

proc = Popen([command], shell=True, text=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

line_found = False
while not line_found:
	line = proc.stdout.readline()
	print(line)
	if line.find("Long dispatch") > -1:
		line_found=True



print("We reached the end of the startup")
time.sleep(1)
print(dir(proc.stdin))
proc.stdin.write(levelcontrol)

line_found = False
while not line_found:
	print(proc.stdout.readline())
	print(proc.stderr.readline())

