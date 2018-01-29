import urllib.request
import xml.etree.ElementTree as ET

# request = 'http://217.61.6.129/th_js_online/php/AlbetetKozoskoltseg.php?albetet_id=';
# year_CONST = '&ev='
year = '2017'
day = '10'

class Requirement:
    def __init__(self,month,date,requiredAmount,payment,monthlyBalance):
        self.id = month;
        self.date = date;
        self.requiredAmount = requiredAmount;
        self.payment = payment;
        self.monthlyBalance = monthlyBalance;
        self.interestRate = 1.0;
        self.totalAmount = self.interestRate * self.requiredAmount;

    def updateInterest(self,interestRate):
        if (interestRate != self.interestRate):
            self.totalAmount /= self.interestRate;
            self.totalAmount *= interestRate;
            self.interestRate = interestRate;

class Payment:
    def __init__(self,date,person,subject,amount):
        self.date = date;
        self.person = person;
        self.subject = subject;
        self.amount = amount;

from datetime import datetime

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

class Person:
    requirements = [];
    payments = [];

    def __init__(self,name,startBalance,requiredAmount,paymentTotal,balance):
        self.name = name;
        self.requiredAmount = requiredAmount;
        self.paymentTotal = paymentTotal
        self.balance = balance
        self.payments = [];
        self.requirements = [];

    def recordRequirement(self,child):
        # print(datetime.strptime(str(year)+' ' + str(child[1].text) + ' ' + str(1), '%Y %m. %d'));
        req = Requirement(
            child[1].text,
            datetime.strptime(str(year)+' ' + str(child[1].text) + ' ' + str(day), '%Y %m. %d'),
            self.valueFromCurrency(child[2].text),
            self.valueFromCurrency(child[3].text),
            self.valueFromCurrency(child[4].text)
        );

        self.requirements.append(req);

        # print('REQUIREMENT RECORDED...');
        for payment in self.payments:
            req.updateInterest(getInterestRate(req.date, payment.date));
            # print('requirement was: ' + str(req.totalAmount) + ' with interest rate of ' + str(req.interestRate) + ', payment: ' + str(payment.amount));
            req.totalAmount -= payment.amount;
            if (req.totalAmount >= 1 ):
                payment.amount = 0;
            else:
                payment.amount = abs(req.totalAmount);

            print('after payment the requirement is: ' + str(req.totalAmount) + ', remaining amount: ' + str(payment.amount) + ', with interestRate: ' + str(req.interestRate));
            if (req.totalAmount <= 1):
                break;
            # print('requirement date: ' + str(req.date) + ', paydate: ' + str(payment.date) + ', delta: ' + str(req.payment.date-req.date));
        # print(len(self.requirements));
        self.requirements = [requirement for requirement in self.requirements if requirement.totalAmount > 1];
        self.payments = [payment for payment in self.payments if payment.amount > 1];

    def recordPayment(self,child):

        # print(datetime.strptime(child[5].text, '%Y.%m.%d'));
        payment = Payment(
            datetime.strptime(child[5].text, '%Y.%m.%d'),
            child[6].text,
            child[7].text,
            self.valueFromCurrency(child[8].text)
        )
        self.payments.append(payment);

        # print('PAYMENT RECORDED...');
        print ('\r\nNew Payment recorded at: ' + str(payment.date) + ', with amount: ' + str(payment.amount)) ;
        for req in self.requirements:
            req.updateInterest(getInterestRate(req.date, payment.date));
            print('requirement was: ' + str(req.totalAmount) + ' with interest rate of ' + str(req.interestRate) + ', payment: ' + str(payment.amount));
            req.totalAmount -= payment.amount;
            if (req.totalAmount >= 1 ):
                payment.amount = 0;
            else:
                payment.amount = abs(req.totalAmount);

            print('after payment the requirement is: ' + str(req.totalAmount) + ', remaining amount: ' + str(payment.amount) + ', with interestRate: ' + str(req.interestRate));
            print('requirement date: ' + str(req.date) + ', paydate: ' + str(payment.date) + ', delta: ' + str(payment.date - req.date));
            if (payment.amount <= 1):
                break;

        # print(len(self.requirements));
        self.requirements = [requirement for requirement in self.requirements if requirement.totalAmount > 1];
        self.payments = [payment for payment in self.payments if payment.amount > 1];
        # print(len(self.requirements));

    def valueFromCurrency(self,string):
        return int(str.split(string,' ')[0]);

def getInterestRate(d1, d2):
    delta = (d2-d1).days;
    if (delta < 31):
        return 1.0;
    elif (delta >= 31 and delta <=45):
        return 1.2;
    elif (delta >= 46 and delta <= 90):
        return 1.4;
    else:
        return 1.6;
    # print('requirement date: ' + str(d1) + ', paydate: ' + str(d2) + ', delta: ' + str(delta.days));

idListFile = 'idList.txt';
idList = [];
with open(idListFile) as f:
    i = 0;
    for line in f:
        if (i%2 == 0):
            idList.append(int(line));
        i+=1;

# print(idList);
# print(len(idList));

out = open('Eredmenyek.txt','w');
for id in idList:
# for id in range(9156,9157):
    strId = str(id);
    # response = urllib.request.urlopen(request+strId+year_CONST+year).read();
    f = open('responses/savedResponse_' +str(id)+ '.txt','r');
    response = f.read();
    f.close();
    root = ET.fromstring(response);
    #
    # f = open('responses/savedResponse_'+str(id)+'.txt','w');
    # f.write(str(response,'utf-8'));
    # f.close();
    person = Person(root[1][1][6].text,root[1][1][8].text,root[1][2][8].text,root[1][3][8].text,root[1][4][8].text)

    LIMIT = 5;
    i = 0;
    for child in root[1]:
        if (i>LIMIT):
            if (child[0].text == '1'):
                person.recordRequirement(child);
            elif (child[0].text =='0'):
                person.recordPayment(child);
        i+=1;

    out.write('\r\n' + person.name+'\n')
    print('\r\n' + person.name);
    sum = 0;


    for req in person.requirements:
        datetime_object = datetime.strptime('01 1 2018', '%m %d %Y')
        req.updateInterest(getInterestRate(req.date, datetime_object ));
        sum += req.totalAmount;
        print(str(req.date) + ', remaining total payment: ' + str(req.totalAmount) + ', interestRate: ' + str(req.interestRate))
        # out.write(str(req.date) + ', remaining total payment: ' + str(req.totalAmount) + ', interestRate: ' + str(req.interestRate) +'\n');

    # print('total unpaid amount: {:.0f} Ft.'.format(sum));
    # out.write('total unpaid amount: {:.0f} Ft.'.format(sum)+'\n')
    #
    print('Teljes tartozás: {:.0f} Ft.'.format(sum));
    out.write('Teljes tartozás: {:.0f} Ft.'.format(sum)+'\n')

out.close();
    # print('ID: ' + strId + ', név: ' + person.name + ', összes befizetés:' + str(sum));




# f = open('savedResponse.txt','w');
# f.write(str(response,'utf-8'));
#
#
# print(response);
# f.close();
#
# f = open('savedResponse.txt','r');
# response = f.read();
# f.close();
# print(response);

# for child in root:
    # print(child.tag,child.attrib)

# print(len(root[1]))
#
# for i in range(0,9):
#     print(str(i) + ' ' + str(root[1][1][i].text))
# print(root.dataset);
# print(root.attrib)
