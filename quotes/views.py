from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .forms import CreateUserForm
from .models import NewStock
from .forms import NewStockForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
import requests
import json
import pandas as pd

def loginPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				messages.info(request, 'Username or Password incorrect')

		context={}
		return render(request, 'login.html', context)

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()

		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				messages.success(request, 'Account created for ' + form.cleaned_data.get('username'))

				return redirect('login')

		context={'form' : form}
		return render(request, 'register.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def home(request):	
	
	
	try:
		#the ticker symbols are given alternatively for nse and bse
		url ="https://query1.finance.yahoo.com/v7/finance/quote?symbols=ADANIPORTS.NS,ADANIPORTS.BO,ASIANPAINT.NS,500820.BO,AXISBANK.NS,532215.BO,BAJAJ-AUTO.NS,BAJAJ-AUTO.BO,BAJFINANCE.NS,BAJFINANCE.BO,BAJAJFINSV.NS,BAJAJFINSV.BO,BHARTIARTL.NS,BHARTIARTL.BO,INFRATEL.NS,INFRATEL.BO,BPCL.NS,BPCL.BO,BRITANNIA.NS,BRITANNIA.BO,CIPLA.NS,500087.BO,COALINDIA.NS,COALINDIA.BO,DRREDDY.NS,DRREDDY.BO,EICHERMOT.NS,EICHERMOT.BO,GAIL.NS,532155.BO,GRASIM.NS,GRASIM.BO,HCLTECH.NS,HCLTECH.BO,HDFC.NS,HDFC.BO,HDFCBANK.NS,HDFCBANK.BO,HEROMOTOCO.NS,HEROMOTOCO.BO,HINDALCO.NS,HINDALCO.BO,HINDUNILVR.NS,HINDUNILVR.BO,ICICIBANK.NS,532174.BO,INDUSINDBK.NS,532187.BO,INFY.NS,INFY.BO,IOC.NS,IOC.BO,ITC.NS,ITC.BO,JSWSTEEL.NS,JSWSTEEL.BO,KOTAKBANK.NS,KOTAKBANK.BO,LT.NS,LT.BO,MARUTI.NS,MARUTI.BO,NESTLEIND.NS,NESTLEIND.BO,NTPC.NS,NTPC.BO,ONGC.NS,ONGC.BO,POWERGRID.NS,POWERGRID.BO,RELIANCE.NS,RELIANCE.BO,SBIN.NS,SBIN.BO,SHREECEM.NS,SHREECEM.BO,SUNPHARMA.NS,SUNPHARMA.BO,TATAMOTORS.NS,TATAMOTORS.BO,TATASTEEL.NS,TATASTEEL.BO,TCS.NS,TCS.BO,TECHM.NS,TECHM.BO,TITAN.NS,TITAN.BO,ULTRACEMCO.NS,ULTRACEMCO.BO,UPL.NS,UPL.BO,VEDL.NS,VEDL.BO,WIPRO.NS,WIPRO.BO,ZEEL.NS,ZEEL.BO,M%26M.NS%2CM%26M.BO"
		response = json.loads((requests.request("GET", url)).content) #pulls data from yahoo finance
		#lists used to store necessary data from the returned data
		df2 = logic(response)
	except Exception as e:
		response="Error"



	return render(request,'home.html',{'api': df2})


@login_required(login_url='login')
def searchPage(request):


	if(request.method == 'POST'):
		ticker = request.POST['ticker']
		url ="https://query1.finance.yahoo.com/v7/finance/quote?symbols="+ticker+".NS,"+ticker+".BO"
		try:
			response = json.loads((requests.request("GET", url)).content) #pulls the data from the api

			#stores all the necessary parameters in respective lists
			name =[]
			bse_ask =[]
			nse_ask =[]
			bse_bid =[]
			nse_bid =[]
			cost =[]

			quotes_len = len(response['quoteResponse']['result'])

			#we need ask and bid values for selling and buying prices respectively
			for i in range(quotes_len):
			    if(i%2==0):
			        nse_ask.append(response['quoteResponse']['result'][i]['ask'])
			        nse_bid.append(response['quoteResponse']['result'][i]['bid'])
			    else:
			        bse_ask.append(response['quoteResponse']['result'][i]['ask'])
			        bse_bid.append(response['quoteResponse']['result'][i]['bid'])
			        name.append(response['quoteResponse']['result'][i]['shortName'])
			    
			diff =[]
			arbitrage =[]
			Colors =[]

			#calculate arbitrage and assign profits 
			for i in range(quotes_len//2):
			    if(nse_ask[i]<=bse_ask[i]):
			        if(nse_ask[i]<bse_bid[i]):
			            diff.append(bse_bid[i]-nse_ask[i])
			            cost.append((bse_bid[i]*0.0001)+(nse_ask[i]*0.0001))
			            Colors.append("nse")

			            
			        else:
			            diff.append(0)
			            cost.append(0)
			            Colors.append(0)

			    else:
			        if(bse_ask[i]<nse_bid[i]):
			            diff.append(nse_bid[i]-bse_ask[i])
			            cost.append((bse_ask[i]*0.0001)+(nse_bid[i]*0.0001))
			            Colors.append("bse")
			        else:
			            diff.append(0)
			            cost.append(0)
			            Colors.append(0)
			    arbitrage.append(diff[i] - cost[i])

			    #you need a dataframe to reurn the values as a row
			df = pd.DataFrame({'Name':name,
			'colors':Colors,
			'NSE_BID':nse_bid,
			'BSE_BID':bse_bid,
			'NSE_ASK':nse_ask,
			'BSE_ASK':bse_ask,
			'DIFF':diff,
			'Arbitrage':arbitrage})

			sorted_df = df.sort_values(by='Arbitrage',kind='mergesort',ascending=False)

			l1 = ['Name','colors','NSE_BID','BSE_BID','NSE_ASK','BSE_ASK','Diff','Arbitrage']
			ans = sorted_df.values.tolist()
			df2 ={}
			for i in range(len(ans)):
			    df2[i] = dict(zip(l1,ans[i]))

		except Exception as e:
			response="Error"



	return render(request,'search_stock.html',{'ticker': df2 })

	


	

@login_required(login_url='login')
def about(request):
	return render(request,'about.html',{})

@login_required(login_url='login')
def add_stock(request):
	#if the use types a ticker symbol in the input bar
	if  request.method == 'POST':
		form = NewStockForm(request.POST)

		if(form.is_valid()):
			post=form.save(commit=False)
			post.user=request.user
			post.save()
			return redirect('add_stock')

		else:
			return render(request,'add_stock.html',{'ticker': "Error" })
	else:
		#display all saved ticker information
		ticker = NewStock.objects.filter(user=request.user)
		ids = []
		str1 =''
		ticker_list=[]
		for ticker_item in ticker:
			ids.append(ticker_item.id)
			ticker_list.append(str(ticker_item))
			str1 += (str(ticker_item)+".NS,"+str(ticker_item)+".BO,")


		url ="https://query1.finance.yahoo.com/v7/finance/quote?symbols="+str1
		df2={}
		try:
			response = json.loads((requests.request("GET", url)).content)
			name =[]
			bse_ask =[]
			nse_ask =[]
			bse_bid =[]
			nse_bid =[]
			cost =[]
			sorted_df = []

			quotes_len = len(response['quoteResponse']['result'])


			for i in range(quotes_len):
			    if(i%2==0):
			        nse_ask.append(response['quoteResponse']['result'][i]['ask'])
			        nse_bid.append(response['quoteResponse']['result'][i]['bid'])
			    else:
			        bse_ask.append(response['quoteResponse']['result'][i]['ask'])
			        bse_bid.append(response['quoteResponse']['result'][i]['bid'])
			        name.append(response['quoteResponse']['result'][i]['shortName'])
			    
			diff =[]
			arbitrage =[]
			Colors =[]

			for i in range(quotes_len//2):
			    if(nse_ask[i]<=bse_ask[i]):
			        if(nse_ask[i]<bse_bid[i]):
			            diff.append(bse_bid[i]-nse_ask[i])
			            cost.append((bse_bid[i]*0.0001)+(nse_ask[i]*0.0001))
			            Colors.append("nse")

			            
			        else:
			            diff.append(0)
			            cost.append(0)
			            Colors.append(0)

			    else:
			        if(bse_ask[i]<nse_bid[i]):
			            diff.append(nse_bid[i]-bse_ask[i])
			            cost.append((bse_ask[i]*0.0001)+(nse_bid[i]*0.0001))
			            Colors.append("bse")
			        else:
			            diff.append(0)
			            cost.append(0)
			            Colors.append(0)
			    arbitrage.append(diff[i] - cost[i])

			df = pd.DataFrame({'Name':name,
			'colors':Colors,
			'NSE_BID':nse_bid,
			'BSE_BID':bse_bid,
			'NSE_ASK':nse_ask,
			'BSE_ASK':bse_ask,
			'DIFF':diff,
			'Arbitrage':arbitrage,
			'og_str':ticker_list})
			
			sorted_df = df.sort_values(by='Arbitrage',kind='mergesort',ascending=False)

			l1 = ['Name','colors','NSE_BID','BSE_BID','NSE_ASK','BSE_ASK','Diff','Arbitrage','og_str']
			ans = sorted_df.values.tolist()
			df2 ={}
			for i in range(len(ans)):
			    df2[i] = dict(zip(l1,ans[i]))


		except Exception as e:
			response="Error"



		return render(request,'add_stock.html',{'ticker': df2 ,'options' : ticker})


@login_required(login_url='login')
def delete_stock(request, stock_name):
	item = NewStock.objects.filter(user=request.user,ticker=stock_name)
	item.delete()
	return  redirect('add_stock')


def logic(response):
	sorted_df = []
	name =[]   
	bse_ask =[]
	nse_ask =[]
	bse_bid =[]
	nse_bid =[]
	cost =[]

	quotes_len = len(response['quoteResponse']['result'])

	#we need ask and bid values for selling and buying prices respectively
	for i in range(quotes_len):
	    if(i%2==0):
	        nse_ask.append(response['quoteResponse']['result'][i]['ask'])
	        nse_bid.append(response['quoteResponse']['result'][i]['bid'])
	    else:
	        bse_ask.append(response['quoteResponse']['result'][i]['ask'])
	        bse_bid.append(response['quoteResponse']['result'][i]['bid'])
	        name.append(response['quoteResponse']['result'][i]['shortName'])
	    
	diff =[]
	arbitrage =[]
	Colors =[]
	#calculate arbitrage and assign profits 
	for i in range(quotes_len//2):
	    if(nse_ask[i]<=bse_ask[i]):
	        if(nse_ask[i]<bse_bid[i]):
	            diff.append(bse_bid[i]-nse_ask[i])
	            cost.append((bse_bid[i]*0.0001)+(nse_ask[i]*0.0001))
	            Colors.append("nse")

	            
	        else:
	            diff.append(0)
	            cost.append(0)
	            Colors.append(0)

	    else:
	        if(bse_ask[i]<nse_bid[i]):
	            diff.append(nse_bid[i]-bse_ask[i])
	            cost.append((bse_ask[i]*0.0001)+(nse_bid[i]*0.0001))
	            Colors.append("bse")
	        else:
	            diff.append(0)
	            cost.append(0)
	            Colors.append(0)
	    arbitrage.append(diff[i] - cost[i])

	#you need a dataframe to reurn the values as a row
	df = pd.DataFrame({'Name':name,
	'colors':Colors,
	'NSE_BID':nse_bid,
	'BSE_BID':bse_bid,
	'NSE_ASK':nse_ask,
	'BSE_ASK':bse_ask,
	'DIFF':diff,
	'Arbitrage':arbitrage})

	sorted_df = df.sort_values(by='Arbitrage',kind='mergesort',ascending=False)

	l1 = ['Name','colors','NSE_BID','BSE_BID','NSE_ASK','BSE_ASK','Diff','Arbitrage']
	ans = sorted_df.values.tolist()
	df2 ={}
	for i in range(len(ans)):
	    df2[i] = dict(zip(l1,ans[i]))

	return df2


