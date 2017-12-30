import csv
import tempfile
from flask import Flask, render_template, redirect, url_for, request, make_response,jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer
import copy
import json
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import pandas as pd


regr = RandomForestRegressor(n_estimators=300,random_state=0)

app = Flask(__name__)

'''

@app.route('/api/post/json', methods=['GET','POST'])
def json_view() :
	data = request.get_json(force=True)
	#print(data)
	df = pd.io.json.json_normalize(data)
	cols=list(df.columns.values)
	#print(df)
	X_train = df.values
	Y_pred=(regr.predict([X_train]))	
	Y_pred=('%.3f' % Y_pred)
	data = Y_pred
	#print(Y_pred)
	response = app.response_class(
		response=json.dumps(data),
		status=200,
		mimetype='application/json'
	)
	return response
	return jsonify(
		Predicted_salary=data,
	)
'''	
@app.route('/')
def form():
	return render_template('index.html')
		
@app.route('/upload', methods=["POST"])
def transform_view():
	file = request.files['data_file']
	if request.method == 'POST':
		
		tempfile_path = tempfile.NamedTemporaryFile().name
		file.save(tempfile_path)
		sheet = pd.read_csv(tempfile_path)
		length=len(sheet.index)
		length2=len(sheet.columns)
		l=length-1
		l2=length2-1
		col=pd.read_csv(tempfile_path, nrows=1).columns.tolist()
		#print(col)
		sheet1=copy.copy(sheet)
		sheet2=copy.copy(sheet)
		X1 = sheet1.iloc[:,:-1].values
		X2 = sheet1.iloc[:,:].values
		X_last=copy.copy(sheet.iloc[l,:-1].values)
		bottom = sheet.tail(1)
		c=col[l2]
		del bottom[c]
		#print(bottom)
		mv=""
		if 'Column Containing Missing Values' in request.form:
			mv=request.form['Column Containing Missing Values']
		else:
			mv=""
		cdv=""
		if 'Column Containing Categorical Values' in request.form:	
			cdv=request.form['Column Containing Categorical Values']
		#print(X2)
		#print(cdv)
		if cdv is not "" and mv is "":
			#print("#printing CDV:\n")
			split_cdv = cdv.split(',')
			#print(split_cdv)
			for i in range(0 , len(split_cdv)):
				elem = int(split_cdv[i])
				c=col[elem]
				dataframe = pd.get_dummies( sheet[c] )
				del sheet[c]
			#print(dataframe)
			sheet= pd.concat([dataframe, sheet], ignore_index=True,axis=1)
			#print(sheet)
			X = sheet.iloc[:,:-1].values
			Y = sheet.iloc[:,-1].values
			X_lastrow= sheet.iloc[l,:-1].values	
		
		if mv is not "" :
			
			mv1=mv.split(',')
			for i in range(0 , len(mv1)):
				elem = int(mv1[i])
				d=elem+1
				imputer=Imputer(missing_values="NaN",strategy="mean",axis=0)
				imputer=imputer.fit(X2[:,elem:d])
				X2[:,elem:d]=imputer.transform(X2[:,elem:d])
			#print("#printing X2",X2)
			sheet3=pd.DataFrame(X2,columns=col)
			X = sheet3.iloc[:,:-1].values
			Y = sheet3.iloc[:,-1].values
			X_lastrow= sheet3.iloc[l,:-1].values
			if cdv is not "" :
				#print("#printing CDV:\n")
				split_cdv = cdv.split(',')
				#print(split_cdv)
				for i in range(0 , len(split_cdv)):
					elem = int(split_cdv[i])
					c=col[elem]
					dataframe = pd.get_dummies( sheet3[c] )
					del sheet3[c]
				#print(dataframe)
				sheet3= pd.concat([dataframe, sheet3], ignore_index=True,axis=1)
				#print(sheet3)
			X = sheet3.iloc[:,:-1].values
			Y = sheet3.iloc[:,-1].values
			X_lastrow= sheet3.iloc[l,:-1].values
		if cdv is "" and mv is "":
			X = sheet.iloc[:,:-1].values
			Y = sheet.iloc[:,-1].values
			X_lastrow= sheet.iloc[l,:-1].values	
		data=request.form
		regr.fit(X,Y)		
		#print(X_last)
		Y_pred=(regr.predict([X_lastrow]))
		#print("#printing Y_pred **************************\n\n")
		#print(Y_pred)
		#print("#printed Y_pred ***************************\n\n")
		Y_pred=('%.3f' % Y_pred)
		#print(Y_pred)
		c=col[l2]
		#print(bottom)
		pred=[]
		pred.append(Y_pred)
		str='Predicted'
		str1=str+' '+c
		bottom[str1] = pd.Series(pred,index=bottom.index)
		
		#return Y_pred
		return render_template("result.html",tables=[sheet2.to_html(classes='sheet')],result=data,res=[bottom.to_html(classes='sheet')])
		return "success"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)