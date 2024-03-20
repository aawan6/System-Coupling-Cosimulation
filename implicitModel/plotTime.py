import matplotlib.pyplot as plt

numSteps = [5, 10, 20, 50, 100]
time1 = [14.49710, 26.69710, 51.00070, 123.62300, 244.41100] #simple engine model 4 participants
time2 = [6.61278, 12.54740, 24.07950, 58.68160, 116.21400] #simple engine model 2 participants
time3 = [0.01952, 0.02201, 0.02451, 0.03166, 0.04765] # main_SimpleTestCase

plt.figure(1)
plt.plot(numSteps, time1, 'r', label='PySyC - 4 Participants')
plt.plot(numSteps, time2, 'g', label='PySyC - 2 Participants')
plt.plot(numSteps, time3, 'b', label='Python')
plt.xlabel('Number of Time Steps')
plt.ylabel('Total Simulation Time [s]')
plt.title('Simple Engine Model Timing')
plt.legend()
plt.show()