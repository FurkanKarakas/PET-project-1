import numpy as np
computationTime = list()
bytesReceived = list()
bytesSent = list()

with open("Alice.txt", "r") as a:
    for line in a:
        lineText = line.split(" ")
        computationTime.append(float(lineText[1]))
        bytesReceived.append(int(lineText[2]))
        bytesSent.append(int(lineText[3]))
with open("Bob.txt", "r") as b:
    for line in b:
        lineText = line.split(" ")
        computationTime.append(float(lineText[1]))
        bytesReceived.append(int(lineText[2]))
        bytesSent.append(int(lineText[3]))

print("Computational cost:")
print("Max:", np.max(computationTime))
print("Min:", np.min(computationTime))
print("Mean:", np.mean(computationTime).round(2))
print("Median:", np.median(computationTime))
print("Std:", np.std(computationTime).round(2))
print()
print("Received bytes:")
print("Max:", np.max(bytesReceived))
print("Min:", np.min(bytesReceived))
print("Mean:", np.mean(bytesReceived).round(2))
print("Median:", np.median(bytesReceived))
print("Std:", np.std(bytesReceived).round(2))
print()
print("Sent bytes:")
print("Max:", np.max(bytesSent))
print("Min:", np.min(bytesSent))
print("Mean:", np.mean(bytesSent).round(2))
print("Median:", np.median(bytesSent))
print("Std:", np.std(bytesSent).round(2))
print()
