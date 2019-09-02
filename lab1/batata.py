import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import iCounter

(c1,c2) = iCounter.exec("example1_o0.dump","example1_o3.dump")


word_c1 = []
frequency_c1 = []
word_c2 = []
frequency_c2 = []

barWidth = 0.3

for i in range(len(c1)):
  word_c1.append(c1[i][0])
  frequency_c1.append(c1[i][1])

for i in range(len(c2)):
  word_c2.append(c2[i][0])
  frequency_c2.append(c2[i][1])

fig, ax = plt.subplots(figsize=(80, 12))
ax.set_yscale('log')

indices = np.arange(len(c1))
rects1 = plt.bar(indices, frequency_c1,  width=barWidth, color='r', label="o0")
rects2 = plt.bar(indices + barWidth, frequency_c2, width=barWidth, color='b', label="o3")

def autolabel(rects):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset['center']*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha['center'], va='bottom')

autolabel(rects1)
autolabel(rects2)

plt.xlabel('Commands')
plt.ylabel('Frequency')
plt.title('Commands frequency for Example 1')
plt.xticks(indices + barWidth /2, word_c1, rotation='vertical')
plt.legend()
plt.savefig('Example1.jpeg')
# plt.show()
