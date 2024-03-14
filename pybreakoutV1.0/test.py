from subprocess import Popen, PIPE
import time
import os
import fcntl

nodeId = "26674"

command = "/home/ubuntu/scripts/matterTool.sh interactive start"
levelcontrol = "levelcontrol subscribe current-level 0 1 " + nodeId + " 2\n"

proc = Popen([command], shell=True, text=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

line_found = False
while not line_found:
	line = proc.stdout.readline()
	print(line)
	if line.find("Long dispatch") > -1:
		line_found=True

print("We reached the end of the startup")
proc.stdout.flush()
proc.stderr.flush()
time.sleep(5)
print(dir(proc.stdin))
proc.stdin.write(levelcontrol)
proc.stdin.close()

line_found = False
while not line_found:

	line = proc.stdout.readline()

	try:
		data_index = line.index("Data =")
	except ValueError:
		data_index = False


	if data_index != False:
		datastream = line.split("Data = ")[1].split(",")[0]
		print(datastream)
