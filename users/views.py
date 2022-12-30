from django.shortcuts import render, HttpResponse
from users.forms import UserRegistrationForm,HeartDataForm
# Create your views here.
from django.contrib import messages
from .models import UserRegistrationModel,HearDataModel
import csv,io
from django_pandas.io import read_frame
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Import tools
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import roc_curve, auc
import numpy as np
import gc
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def UserRegisterAction(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            # return HttpResponseRedirect('./CustLogin')
            form = UserRegistrationForm()
            return render(request, 'Register.html', {'form': form})
        else:
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'Register.html', {'form': form})


def UserLogin(request):
    return render(request, 'UserLogin.html', {})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
            # return render(request, 'user/userpage.html',{})
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})
def BrowseCSV(request):
    return render(request,'users/BrowseCsv.html',{})

def UploadCSVToDataBase(request):
    # declaring template
    template = "users/UserHomePage.html"
    data = HearDataModel.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address,    phone, profile',
        'profiles': data
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')

    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = HearDataModel.objects.update_or_create(
        age=column[0],
        sex=column[1],
        cp=column[2],
        trestbps=column[3],
        chol=column[4],
        fbs=column[5],
        restecg=column[6],
        thalach=column[7],
        exang=column[8],
        oldpeak=column[9],
        slope=column[10],
        ca=column[11],
        thal=column[12],
        target=column[13]

    )
    context = {}

    return render(request, 'users/UserHomePage.html', context)


def DataPreparations(request):
    gc.collect()
    qs = HearDataModel.objects.all()
    df = read_frame(qs)
    print('######First Five Records Of DataSet')
    print(df.head())
    print('###Dataset Description with datatypes')
    print(df.info())
    df.isnull().sum()
    print('Data frame Shape')
    print(df.shape)
    print('Descriptions like means  etc....')
    print(df.describe())
    print('Target Variable Count')
    print(df.target.value_counts())
    print('Data Visulations is ')

    #Box Plot Visualtion
    df.boxplot(by='sex', column=['target'], grid=False)
    #sns.boxplot(by='sex', column=['target'], grid=False)
    # grid = sns.FacetGrid(train_df, col='Pclass', hue='Gender')
    #grid = sns.FacetGrid(df, row='cp', col='ca', size=2.2, aspect=1.6)
    #grid.map(plt.hist, 'age', alpha=.5, bins=20)
    #grid.add_legend()
    corr = df.corr()
    plt.figure(figsize=(18, 10))
    sns.heatmap(corr, annot=True)
    plt.show()
    sns.countplot(df.target, palette=['green', 'red'])
    plt.title("[0] == Not Disease, [1] == Disease");

    plt.figure(figsize=(18, 10))
    sns.countplot(x='age', hue='target', data=df, palette=['#1CA53B', 'red'])
    plt.legend(["Haven't Disease", "Have Disease"])
    plt.title('Heart Disease Frequency for Ages')
    plt.xlabel('age')
    plt.ylabel('Frequency')
    plt.show()

    # sns.set_style("whitegrid")
    plt.figure(figsize=(18, 10))
    sns.distplot(df.age[df['target'] == 0], bins=30, color='#1CA53B', label='Not Disease')
    sns.distplot(df.age[df['target'] == 1], bins=30, color='red', label='Disease')
    plt.legend()
    plt.title('Heart Disease Distribution for Ages')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.show()

    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    fs = ['cp', 'fbs', 'restecg', 'exang', 'slope', 'ca']
    for i, axi in enumerate(axes.flat):
        sns.countplot(x=fs[i], hue='target', data=df, palette='bwr', ax=axi)
        axi.set(ylabel='Frequency')
        axi.legend(["Haven't Disease", "Have Disease"])

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='trestbps', y='thalach', data=df, hue='target')
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='chol', y='thalach', data=df, hue='target')
    plt.show()

    plt.scatter(x=df.age[df.target == 1], y=df.thalach[(df.target == 1)], c="red")
    plt.scatter(x=df.age[df.target == 0], y=df.thalach[(df.target == 0)])
    plt.legend(["Disease", "Not Disease"])
    plt.xlabel("Age")
    plt.ylabel("Maximum Heart Rate")
    plt.show()

    #window.close()
    layout = None
    #window = None
    gc.collect()


    return render(request,'users/DataPreparations.html',{'data':qs})

def UserMachineLearning(request):
    gc.collect()
    qs = HearDataModel.objects.all()
    df = read_frame(qs)

    # Define our feasures and leabels
    X = df.drop(['target'], axis=1).values
    y = df['target'].values

    scale = StandardScaler()
    X = scale.fit_transform(X)
    ### Randome Forest Algorithm
    from sklearn.ensemble import RandomForestClassifier

    clf = Model(model=RandomForestClassifier(), X=X, y=y)
    clf.crossValScore(cv=10)

    clf.accuracy()
    clf.confusionMatrix()
    clf.classificationReport()

    ### Decesion Treee
    from sklearn.tree import DecisionTreeClassifier
    dt = Model(model=DecisionTreeClassifier(),X=X,y=y)
    dt.crossValScore(cv=10)

    dt.accuracy()
    dt.confusionMatrix()
    dt.classificationReport()


    #SVM Algorithm
    from sklearn.svm import SVC

    svm = Model(model=SVC(C=5, probability=True), X=X, y=y)
    svm.crossValScore(cv=10)
    svm.accuracy()
    svm.confusionMatrix()
    svm.classificationReport()

    ## Pipe Line
    import warnings
    warnings.simplefilter("ignore")

    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import QuantileTransformer

    lr = LogisticRegression()
    pipeline = make_pipeline(QuantileTransformer(output_distribution='normal'), lr)

    #lg = Model(model=pipeline, X=X, y=y)
    lg = Model(model=lr, X=X, y=y)
    lg.crossValScore()
    lg.accuracy()
    lg.confusionMatrix()
    lg.classificationReport()

    ### KNN Algorithm
    from sklearn.neighbors import KNeighborsClassifier

    knn = Model(model=KNeighborsClassifier(n_neighbors=100), X=X, y=y)
    knn.crossValScore()
    knn.accuracy()
    knn.confusionMatrix()
    knn.classificationReport()
    ## comparison

    models = [clf, svm, lg, knn,dt]
    for model in models[:2]:
        model.rocCurve()

    models = [clf, svm, lg, knn,dt]
    for model in models[2:]:
        model.rocCurve()

    models = [clf, svm, lg, knn,dt]
    names = []
    accs = []
    rsltdict = {}
    for model in models:
        accura = model.accuracy()
        modelname = model.model_str()
        accs.append(accura);
        names.append(modelname);
        rsltdict.update({modelname:accura})

    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 5))
    plt.yticks(np.arange(0, 1.2, 0.1))
    plt.ylabel("Accuracy")
    plt.xlabel("Algorithms")
    sns.barplot(x=names, y=accs)
    plt.savefig('models_accuracy.png')
    plt.show()

    #window.close()
    layout = None
    #window = None
    gc.collect()

    return render(request,'users/UserMachineLearning.html',{'rsltdict':rsltdict})


class Model:
    def __init__(self, model, X, y):
        self.model = model
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.5,
                                                                                random_state=42)

        self.model.fit(self.X_train, self.y_train)
        print(f"{self.model_str()} Model Trained..")
        self.y_pred = self.model.predict(self.X_test)

    def model_str(self):
        return str(self.model.__class__.__name__)

    def crossValScore(self, cv=5):
        print(self.model_str() + "\n" + "=" * 60)
        scores = ["accuracy", "precision", "recall", "roc_auc"]
        for score in scores:
            cv_acc = cross_val_score(self.model,
                                     self.X_train,
                                     self.y_train,
                                     cv=cv,
                                     scoring=score).mean()

            print("Model " + score + " : " + "%.3f" % cv_acc)

    def accuracy(self):
        accuarcy = accuracy_score(self.y_test, self.y_pred)
        print(self.model_str() + " Model " + "Accuracy is: "+str(accuarcy))
        return accuarcy

    def confusionMatrix(self):
        plt.figure(figsize=(5, 5))
        mat = confusion_matrix(self.y_test, self.y_pred)
        sns.heatmap(mat.T, square=True,
                    annot=True,
                    cbar=False,
                    xticklabels=["Haven't Disease", "Have Disease"],
                    yticklabels=["Haven't Disease", "Have Disease"])

        plt.title(self.model_str() + " Confusion Matrix")
        plt.xlabel('Predicted Values')
        plt.ylabel('True Values');
        plt.show();

    def classificationReport(self):
        print(self.model_str() + " Classification Report" + "\n" + "=" * 60)
        print(classification_report(self.y_test,
                                    self.y_pred,
                                    target_names=['Non Disease', 'Disease']))

    def rocCurve(self):
        y_prob = self.model.predict_proba(self.X_test)[:, 1]
        fpr, tpr, thr = roc_curve(self.y_test, y_prob)
        lw = 2
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr,
                 color='darkorange',
                 lw=lw,
                 label="Curve Area = %0.3f" % auc(fpr, tpr))
        plt.plot([0, 1], [0, 1], color='green',
                 lw=lw, linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(self.model_str() + ' Receiver Operating Characteristic Plot')
        plt.legend(loc="lower right")
        plt.show()


def UserDataView(request):
    data_list = HearDataModel.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(data_list, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'users/DataView_list.html', {'users': users})


def UserAddData(request):
    if request.method == 'POST':
        form = HeartDataForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            age = form.cleaned_data['age']
            sex =  form.cleaned_data['sex']
            cp = form.cleaned_data['cp']
            trestbps = form.cleaned_data['trestbps']
            chol = form.cleaned_data['chol']
            fbs = form.cleaned_data['fbs']
            restecg = form.cleaned_data['restecg']
            thalach = form.cleaned_data['thalach']
            exang = form.cleaned_data['exang']
            oldpeak = form.cleaned_data['oldpeak']
            slope = form.cleaned_data['slope']
            ca = form.cleaned_data['ca']
            thal = form.cleaned_data['thal']

            test_set = [age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]

            #dataset = HeartDataModel.objects.all()
            from django.conf import settings
            import os
            path = os.path.join(settings.MEDIA_ROOT, 'heart.csv')
            dataset = pd.read_csv(path) #pd.read_csv("http://localhost:8000/media/heart.csv")

            #print(dataset.head())

            X = dataset.iloc[:,:-1].values
            y = dataset.iloc[:,-1].values
            X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.20, random_state=0)
            #Logistic Regression
            from sklearn.linear_model import LogisticRegression
            lr = LogisticRegression()
            lr.fit(X_train, Y_train)
            result = lr.predict([test_set])
            rslt = ''
            if result[0] == 0:
                rslt = "You are not suffering from Heart Disease"
            else:
                rslt = "You are suffering from Heart Disease"
            form = HeartDataForm()
            return render(request, 'users/UserAddData.html', {'form': form,'result':rslt})
            # form.save()
            # messages.success(request, 'Data Added Successfull')
            # # return HttpResponseRedirect('./CustLogin')
            # form = HeartDataForm()
            # return render(request, 'users/UserAddData.html', {'form': form})
        else:
            print("Invalid form")
    else:
        form = HeartDataForm()
    return render(request, 'users/UserAddData.html', {'form': form})
