import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn import linear_model, decomposition
from sklearn.metrics import confusion_matrix
from credit_card_data import read_data

pd.set_printoptions(max_rows=25, max_columns=21)
cm = plt.get_cmap('gist_rainbow')

df = read_data()

# print "Anomalies when field3 is Negative"
# field3_negative =  df[df.field3 < 0 ]['anomaly']
# grouped = field3_negative.value_counts()
# print "%2d/100" % (100 * (float(grouped.values.min())/grouped.values.max()))
# print

# print "Anomalies when field3 is Positive"
# field3_positive = df[df.field3 >= 0]['anomaly']
# grouped = field3_positive.value_counts()
# print "%2d/100" % (100 * (float(grouped.values.min())/grouped.values.max()))
# print

# # test if subset w/ negative `field3` as 
# # significantly different distribution of anomalies
# # if P <= 0.05, the distributions are significantly different
# Z_statistic, P = stats.ranksums(x=field3_negative, y=field3_positive)
# print "Tested if subset with `field3` < 0 has different distribution of anomalies"
# print "\tdistributions are significantly different if P <= 0.05"
# print "\tP => %f" % P

def call(frame, func, *args):
	func(frame, *args)

def make_scatter(frame, x_y, colour=None):
	"""scatters two number columns on a dataframe"""	
	x, y = x_y

	fig = plt.figure(figsize=(10, 5))
	ax = fig.add_subplot("111")

	if colour is not None:
		colours = frame[colour].unique() 
		frame = frame.groupby(colour).reset_index()
		
		ax.set_color_cycle([cm(1.*i/len(colours)) for i in range(len(colours))])
		
		for i, colour in enumerate(colours):
			rgb = cm(1.* i /len(colours))
			X = frame.ix[(colour)][x]
			Y = frame.ix[(colour)][y]

			ax.scatter(X, Y, marker='o', c=rgb, s=20, alpha=0.75)
		
		ax.legend(colours)

	else:
		pass
	
	ax.set_xlabel(x.title())
	ax.set_ylabel(y.title())
	plt.show()
	plt.clf()

# make_scatter(df, x_y=("field3", "amount"), colour="anomaly")

plot_funcs = [ (make_scatter,df,( ("field3", "amount"), "anomaly")),
			   (make_scatter,df,( ("total", "amount"), "anomaly")) ]


logistic = linear_model.LogisticRegression()
pca = decomposition.PCA()

pipe = Pipeline(steps=[('pca', pca), ('logistic', logistic)])

target 	 = 'anomaly'

features = [col for col in df.columns if col != target 
			and df[col].dtype not in (str, object)]

max_features = len(features)
n_components = range(max_features)
Cs = np.logspace(-4, 4, 3)

pca.fit(df[features])

plt.figure(1, figsize=(4, 3))
plt.clf()
plt.axes([.2, .2, .7, .7])
plt.plot(pca.explained_variance_, linewidth=2)
plt.axis('tight')
plt.xlabel('n_components')
plt.ylabel('explained_variance_')

est = GridSearchCV(pipe, dict(pca__n_components=n_components,logistic__C=Cs))

est.fit(df[features], df[target])

plt.axvline(est.best_estimator_.named_steps['pca'].n_components,
           linestyle=':', label='n_components chosen')

plt.legend(prop=dict(size=12))


confusion = confusion_matrix(df.anomaly, est.predict(df[features]))

confusion = pd.DataFrame(confusion, index=['Actual 0', 'Actual 1'], 
				columns=['Predicted 0', 'Predicted 1'])

print confusion




