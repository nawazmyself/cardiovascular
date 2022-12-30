from django.shortcuts import render,HttpResponse
from django.contrib import messages
from users.models import UserRegistrationModel,HearDataModel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, HttpResponse
from users.forms import UserRegistrationForm,HeartDataForm
# Create your views here.
from django.contrib import messages


from django_pandas.io import read_frame
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from sklearn.preprocessing import StandardScaler

# Import tools
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import roc_curve, auc
import numpy as np
import gc
# Create your views here.
def AdminLogin(request):
    return render(request,'AdminLogin.html',{})

def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')

        else:
            messages.success(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html',{})
def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request,'admins/ViewRegisterUsers.html',{'data':data})

def ActivaUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request,'admins/ViewRegisterUsers.html',{'data':data})

def AdminDataView(request):
    data_list = HearDataModel.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(data_list, 15)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'admins/AdminDataView.html', {'data': data})


def AdminMachineLearning(request):

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

    return render(request,'admins/AdminMachineLearning.html',{'rsltdict':rsltdict})

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


