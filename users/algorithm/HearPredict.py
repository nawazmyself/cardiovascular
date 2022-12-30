# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 15:17:04 2018

@author: v-sojag
"""
# Importing all the libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()
# Step 1: Exploratory Data Analysis

# Read the data file
dataset = pd.read_csv('heart.csv')

# Check columns and rows in the data
dataset.shape
# Check data type of data
dataset.info()
# See top 5 rows
print(dataset.head(15))
# Check bottom 5 rows
dataset.tail()
# Check sample of any 5 rows
dataset.sample(5)

# Print the main matrices for the data
dataset.describe()

# get the number of missing data points per column. This will show up in variable explorer
missing_values_count = dataset.isnull().sum()
# look at/print the # of missing points in the first ten columns
missing_values_count[0:16]

# Print unique values of all the columns
dataset.age.unique()
dataset.cp.unique()
dataset.trestbps.unique()

# Plot only the values of num- the value to be predicted/Label
dataset["age"].value_counts().sort_index().plot.bar()

# Heat map to see the coreelation between variables, use annot if you want to see the values in the heatmap
plt.subplots(figsize=(12, 8))
sns.heatmap(dataset.corr(), robust=True, annot=True)
# CONCLUSION: Ignoring ID since it was manually added
# Positive correlation: num vs cp, exang vs cp,num vs exang, old peak vs exang,
# Negative orelation:Age vs thalach,cp vs thalach,exang vs thalach,num vs thalach

# custom correlogram
sns.pairplot(dataset, hue="age")

# Histogram for all features
dataset.hist(figsize=(15, 12), bins=20, color="#007959AA")
plt.title("Features Distribution")
plt.show()

# Step 2: Defining X,y, train and test

# Plot before - Detect and remove outliers
plt.subplots(figsize=(15, 6))
dataset.boxplot(patch_artist=True, sym="k.")
# plt.xticks(rotation=90)

# Defining X and y
X = dataset.iloc[:, 1: 11].values
y = dataset.iloc[:, -2].values

# Feature Scaling
from sklearn.preprocessing import StandardScaler

sc_X = StandardScaler()
sc_y = StandardScaler()
X = sc_X.fit_transform(X)
y = sc_y.fit_transform(y)

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

# Taking care of nans
from sklearn.preprocessing import Imputer

imputer = Imputer(strategy='mean')
imputer = imputer.fit(X[:, 4:11])
X[:, 4:11] = imputer.transform(X[:, 4:11])

# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Dense

# Step 3: Initialising the ANN
classifier = Sequential()

# Adding the input layer and the first hidden layer
classifier.add(Dense(output_dim=6, init='uniform', activation='relu', input_dim=10))

# Adding the second hidden layer
classifier.add(Dense(output_dim=6, init='uniform', activation='relu'))

# Adding the output layer
classifier.add(Dense(output_dim=1, init='uniform', activation='sigmoid'))

# Compiling the ANN
classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Fitting the ANN to the Training set
classifier.fit(X_train, y_train, batch_size=10, nb_epoch=100)

# Part 3 - Making the predictions and evaluating the model

# Predicting the Test set results
y_pred = classifier.predict(X_test)
y_pred = (y_pred > 0.5)

# Making the Confusion Matrix
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)

# Part 4 - Evaluating, Improving and Tuning the ANN

# Evaluating the ANN
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from keras.models import Sequential
from keras.layers import Dense


def build_classifier():
    classifier = Sequential()
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=10))
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))
    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return classifier


classifier = KerasClassifier(build_fn=build_classifier, batch_size=10, epochs=100)
accuracies = cross_val_score(estimator=classifier, X=X_train, y=y_train, cv=10, n_jobs=-1)
mean = accuracies.mean()
variance = accuracies.std()

# Improving the ANN
# Dropout Regularization to reduce overfitting if needed

# Part 5: Tuning the ANN
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
from keras.models import Sequential
from keras.layers import Dense


def build_classifier(optimizer):
    classifier = Sequential()
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=10))
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))
    classifier.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return classifier


classifier = KerasClassifier(build_fn=build_classifier)
parameters = {'batch_size': [25, 32],
              'epochs': [100, 500],
              'optimizer': ['adam', 'rmsprop']}
grid_search = GridSearchCV(estimator=classifier,
                           param_grid=parameters,
                           scoring='accuracy',
                           cv=10)
grid_search = grid_search.fit(X_train, y_train)
best_parameters = grid_search.best_params_
best_accuracy = grid_search.best_score_




