from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
# import ipfs
import ipfshttpclient

import os
from django.core.files.storage import FileSystemStorage
import pickle

global details, username
details=''
global contract

# api = ipfshttpclient.connection(host='http://127.0.0.1', port=5001)

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Ecommerce.json' #ecommerce contract code
    deployed_contract_address = '0xc6FB932c552c03F56C22cdB0ead7D2298bD19286' #hash address to access student contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'signup':
        details = contract.functions.getUser().call()
    if contract_type == 'addproduct':
        details = contract.functions.getProduct().call()
    if contract_type == 'bookorder':
        details = contract.functions.getOrder().call()    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Ecommerce.json' #ecommerce contract file
    deployed_contract_address = '0xc6FB932c552c03F56C22cdB0ead7D2298bD19286' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'signup':
        details+=currentData
        msg = contract.functions.addUser(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'addproduct':
        details+=currentData
        msg = contract.functions.addProduct(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'bookorder':
        details+=currentData
        msg = contract.functions.bookOrder(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def updateQuantityBlock(currentData):
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Ecommerce.json' #student contract file
    deployed_contract_address = '0xc6FB932c552c03F56C22cdB0ead7D2298bD19286' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    msg = contract.functions.addProduct(currentData).transact()
    tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    
def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def BrowseProducts(request):
    if request.method == 'GET':
        output = '<tr><td><font size="" color="black">Product&nbsp;Name</font></td><td><select name="t1">'
        readDetails("addproduct")
        rows = details.split("\n")
        productsList = []
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'addproduct' and arr[2] not in productsList:
                productsList.append(arr[2])
                output+='<option value="'+arr[2]+'">'+arr[2]+'</option>'
        output+="</select></td></tr>"
        context= {'data1':output}
        return render(request, 'BrowseProducts.html', context)

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def ViewHistory(request):
    if request.method == 'GET':
        global details
        user = ''
        userlist = []
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Seller Name</font></th>'
        output+='<th><font size=3 color=black>Product Name</font></th>'
        output+='<th><font size=3 color=black>Customer Name</font></th>'
        output+='<th><font size=3 color=black>Contact No</font></th>'
        output+='<th><font size=3 color=black>Email ID</font></th>'
        output+='<th><font size=3 color=black>Address</font></th>'
        output+='<th><font size=3 color=black>Ordered Date</font></th></tr>'
        readDetails("bookorder")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'bookorder' and (arr[1] == user or arr[3] == user):
                print(arr[2]+" "+user)
                details = arr[4].split(",")
                pid = arr[2]
                customer = arr[3]
                book_date = arr[5]
                if arr[1] not in userlist:
                    userlist.append(arr[1])
                    output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
                    output+='<td><font size=3 color=black>'+pid+'</font></td>'
                    output+='<td><font size=3 color=black>'+customer+'</font></td>'
                    output+='<td><font size=3 color=black>'+details[0]+'</font></td>'
                    output+='<td><font size=3 color=black>'+details[1]+'</font></td>'
                    output+='<td><font size=3 color=black>'+details[2]+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(book_date)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'ConsumerScreen.html', context)     
    
def ViewOrders(request):
    if request.method == 'GET':
        global details
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Seller Name</font></th>'
        output+='<th><font size=3 color=black>Product Name</font></th>'
        output+='<th><font size=3 color=black>Customer Name</font></th>'
        output+='<th><font size=3 color=black>Contact No</font></th>'
        output+='<th><font size=3 color=black>Email ID</font></th>'
        output+='<th><font size=3 color=black>Address</font></th>'
        output+='<th><font size=3 color=black>Ordered Date</font></th></tr>'
        readDetails("bookorder")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'bookorder' and arr[1] == user:
                print(arr[2]+" "+user)
                details = arr[4].split(",")
                pid = arr[2]
                customer = arr[3]
                book_date = arr[5]
                output+='<tr><td><font size=3 color=black>'+user+'</font></td>'
                output+='<td><font size=3 color=black>'+pid+'</font></td>'
                output+='<td><font size=3 color=black>'+customer+'</font></td>'
                output+='<td><font size=3 color=black>'+details[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+details[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+details[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(book_date)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'ViewOrders.html', context)     

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def AddProduct(request):
    if request.method == 'GET':
       return render(request, 'AddProduct.html', {})

def SaleProductAction(request):
    if request.method == 'GET':
        global details
        supplier = request.GET['t1']
        product = request.GET['t2']
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            #print("my=== "+str(arr[0])+" "+arr[1]+" "+arr[2]+" "+ptype)
            if arr[0] == 'addproduct':
                if arr[2] == product and arr[1] == supplier:
                    record = arr[0]+"#"+user+"#"+arr[2]+"#"+arr[3]+"#1#"+arr[5]+"#"+arr[6]+"#Second Sale\n"
                    saveDataBlockChain(record,"addproduct")
        context= {'data':"Your Product put on Sale. You can see View History to know about purchaser"}
        return render(request, 'ConsumerScreen.html', context)            
                    

# def SaleProduct(request):
#     if request.method == 'GET':
#         output = '<table border=1 align=center>'
#         output+='<tr><th><font size=3 color=black>Second Seller Name</font></th>'
#         output+='<th><font size=3 color=black>Product Name</font></th>'
#         output+='<th><font size=3 color=black>Price</font></th>'
#         output+='<th><font size=3 color=black>Quantity</font></th>'
#         output+='<th><font size=3 color=black>Description</font></th>'
#         output+='<th><font size=3 color=black>Image</font></th>'
#         output+='<th><font size=3 color=black>Sale Your Product</font></th></tr>'
#         user = ''
#         with open("session.txt", "r") as file:
#             for line in file:
#                 user = line.strip('\n')
#         file.close()
#         readDetails("bookorder")
#         bookorder = details
#         readDetails("addproduct")
#         orders = bookorder.split("\n")
#         rows = details.split("\n")
#         for k in range(len(orders)-1):
#             order_arr = orders[k].split("#")
#             if order_arr[0] == 'bookorder':
#                 pid = order_arr[2]
#                 if order_arr[3] == user:
#                     userList = []
#                     for i in range(len(rows)-1):
#                         arr = rows[i].split("#")
#                         if arr[0] == 'addproduct':
#                             if arr[2] == pid and user == order_arr[3] and user not in userList and (arr[7] == 'Fresh Sale' or arr[7] == 'Second Sale'):
#                                 userList.append(user)
#                                 output+='<tr><td><font size=3 color=black>'+order_arr[3]+'</font></td>'
#                                 output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
#                                 output+='<td><font size=3 color=black>'+str(arr[3])+'</font></td>'
#                                 output+='<td><font size=3 color=black>1</font></td>'
#                                 output+='<td><font size=3 color=black>'+arr[5]+'</font></td>'
#                                 content = api.get_pyobj(arr[6])
#                                 content = pickle.loads(content)
#                                 if os.path.exists('EcommerceApp/static/product.png'):
#                                     os.remove('EcommerceApp/static/product.png')
#                                 with open('EcommerceApp/static/product.png', "wb") as file:
#                                     file.write(content)
#                                 file.close()
#                                 output+='<td><img src="/static/product.png" width="200" height="200"></img></td>'
#                                 output+='<td><a href=\"SaleProductAction?t1='+arr[1]+'&t2='+arr[2]+'"\'><font size=3 color=black>Click Here</font></a></td></tr>'
#         output+="</table><br/><br/><br/><br/><br/><br/>"
#         context= {'data':output}
#         return render(request, 'ConsumerScreen.html', context)      





def SaleProduct(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output += '<tr><th><font size=3 color=black>Second Seller Name</font></th>'
        output += '<th><font size=3 color=black>Product Name</font></th>'
        output += '<th><font size=3 color=black>Price</font></th>'
        output += '<th><font size=3 color=black>Quantity</font></th>'
        output += '<th><font size=3 color=black>Description</font></th>'
        output += '<th><font size=3 color=black>Image</font></th>'
        output += '<th><font size=3 color=black>Sale Your Product</font></th></tr>'
        
        # Read the user from session.txt
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        
        # Read product and order details
        readDetails("bookorder")
        bookorder = details
        readDetails("addproduct")
        orders = bookorder.split("\n")
        rows = details.split("\n")
        
        # Loop through each order and match the relevant product
        for k in range(len(orders)-1):
            order_arr = orders[k].split("#")
            if order_arr[0] == 'bookorder':
                pid = order_arr[2]
                if order_arr[3] == user:
                    userList = []
                    for i in range(len(rows)-1):
                        arr = rows[i].split("#")
                        if arr[0] == 'addproduct':
                            if arr[2] == pid and user == order_arr[3] and user not in userList and (arr[7] == 'Fresh Sale' or arr[7] == 'Second Sale'):
                                userList.append(user)
                                output += f'<tr><td><font size=3 color=black>{order_arr[3]}</font></td>'
                                output += f'<td><font size=3 color=black>{arr[2]}</font></td>'
                                output += f'<td><font size=3 color=black>{arr[3]}</font></td>'
                                output += f'<td><font size=3 color=black>1</font></td>'
                                output += f'<td><font size=3 color=black>{arr[5]}</font></td>'
                                
                                try:
                                    # Using the correct method `get()` to retrieve the file from IPFS
                                    content = api.get(arr[6])  # arr[6] is expected to be the IPFS hash
                                    if content:
                                        content = content['Content']  # Extract the content from the response
                                        
                                        # Remove the existing product image if it exists
                                        if os.path.exists('EcommerceApp/static/product.jpg'):
                                            os.remove('EcommerceApp/static/product.jpg')
                                        
                                        # Write the image content to a file
                                        with open('EcommerceApp/static/product.jpg', "wb") as file:
                                            file.write(content)
                                        file.close()
                                        
                                        output += f'<td><img src="/static/product.jpg" width="200" height="200"></img></td>'
                                    else:
                                        output += '<td><font size=3 color=black>No image</font></td>'
                                except Exception as e:
                                    output += f'<td><font size=3 color=black>Error loading image</font></td>'
                                    print(f"Error retrieving image from IPFS: {e}")
                                
                                output += f'<td><a href="SaleProductAction?t1={arr[1]}&t2={arr[2]}"><font size=3 color=black>Click Here</font></a></td></tr>'
        
        output += "</table><br/><br/><br/><br/><br/><br/>"
        context = {'data': output}
        return render(request, 'ConsumerScreen.html', context)





def BookOrder(request):
    if request.method == 'GET':
        global details
        supplier = request.GET['farmer']
        pid = request.GET['crop']
        sale_type = request.GET['t3']
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == user:
                    details = arr[3]+","+arr[4]+","+arr[5]
                    break
        today = date.today()            
        data = "bookorder#"+supplier+"#"+pid+"#"+user+"#"+details+"#"+str(today)+"\n"
        saveDataBlockChain(data,"bookorder")
        if sale_type == 'Second Sale':
            index = 0
            record = ''
            readDetails("addproduct")
            rows = details.split("\n")
            for i in range(len(rows)-1):
                arr = rows[i].split("#")
                if arr[0] == "addproduct":
                    if arr[1] == supplier and arr[2] == pid and arr[7] == 'Second Sale':
                        index = i
                        record = arr[0]+"#"+arr[1]+"#"+arr[2]+"#"+arr[3]+"#"+arr[4]+"#"+arr[5]+"#"+arr[6]+"#Sold\n"
                        break
            for i in range(len(rows)-1):
                if i != index:
                    record += rows[i]+"\n"
            updateQuantityBlock(record)  
        output = 'Your Order details Updated<br/>'
        context= {'data':output}
        return render(request, 'ConsumerScreen.html', context)      

def UpdateQuantity(request):
    if request.method == 'GET':
        output = ''
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()        
        output = '<tr><td><font size="" color="black">Product&nbsp;Name</font></td><td><select name="t1">'
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "addproduct" and arr[7] == 'Fresh Sale':
                if arr[1] == user:
                    output+='<option value="'+arr[2]+'">'+arr[2]+'</option>'
        output+="</select></td></tr>"
        context= {'data':output}
        return render(request, 'UpdateQuantity.html', context)       
        

# def SearchProductAction(request):
#     if request.method == 'POST':
#         ptype = request.POST.get('t1', False)
#         output = '<table border=1 align=center>'
#         output+='<tr><th><font size=3 color=black>Supplier Name</font></th>'
#         output+='<th><font size=3 color=black>Product Name</font></th>'
#         output+='<th><font size=3 color=black>Price</font></th>'
#         output+='<th><font size=3 color=black>Quantity</font></th>'
#         output+='<th><font size=3 color=black>Description</font></th>'
#         output+='<th><font size=3 color=black>Image</font></th>'
#         output+='<th><font size=3 color=black>Sale Type</font></th>'
#         output+='<th><font size=3 color=black>Purchase Product</font></th></tr>'
#         readDetails("addproduct")
#         rows = details.split("\n")
#         for i in range(len(rows)-1):
#             arr = rows[i].split("#")
#             print("my=== "+str(arr[0])+" "+arr[1]+" "+arr[2]+" "+ptype)
#             if arr[0] == 'addproduct':
#                 if arr[2] == ptype and (arr[7] == 'Fresh Sale' or arr[7] == 'Second Sale'):
#                     output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
#                     output+='<td><font size=3 color=black>'+str(arr[2])+'</font></td>'
#                     if arr[7] == 'Fresh Sale':
#                         output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
#                     else:
#                         price = float(arr[3])
#                         price = (price / 100) * 80
#                         output+='<td><font size=3 color=black>'+str(price)+'</font></td>'
#                     output+='<td><font size=3 color=black>'+str(arr[4])+'</font></td>'
#                     output+='<td><font size=3 color=black>'+arr[5]+'</font></td>'
#                     content = api.get_pyobj(arr[6])
#                     content = pickle.loads(content)
#                     if os.path.exists('EcommerceApp/static/product.png'):
#                         os.remove('EcommerceApp/static/product.png')
#                     with open('EcommerceApp/static/product.png', "wb") as file:
#                         file.write(content)
#                     file.close()
#                     output+='<td><img src="/static/product.png" width="200" height="200"></img></td>'
#                     output+='<td><font size=3 color=black>'+arr[7]+'</font></td>'
#                     output+='<td><a href=\'BookOrder?farmer='+arr[1]+'&crop='+arr[2]+'&t3='+arr[7]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
#         output+="</table><br/><br/><br/><br/><br/><br/>"
#         context= {'data':output}
#         return render(request, 'SearchProducts.html', context)






def SearchProductAction(request):
    if request.method == 'POST':
        ptype = request.POST.get('t1', False)
        output = '<table border=1 align=center>'
        output += '<tr><th><font size=3 color=black>Supplier Name</font></th>'
        output += '<th><font size=3 color=black>Product Name</font></th>'
        output += '<th><font size=3 color=black>Price</font></th>'
        output += '<th><font size=3 color=black>Quantity</font></th>'
        output += '<th><font size=3 color=black>Description</font></th>'
        output += '<th><font size=3 color=black>Image</font></th>'
        output += '<th><font size=3 color=black>Sale Type</font></th>'
        output += '<th><font size=3 color=black>Purchase Product</font></th></tr>'
        
        # Assuming readDetails() function is implemented to read product details from a source like a file
        readDetails("addproduct")
        
        rows = details.split("\n")
        for i in range(len(rows) - 1):
            arr = rows[i].split("#")
            print(f"my=== {arr[0]} {arr[1]} {arr[2]} {ptype}")
            
            if arr[0] == 'addproduct':
                if arr[2] == ptype and (arr[7] == 'Fresh Sale' or arr[7] == 'Second Sale'):
                    output += f'<tr><td><font size=3 color=black>{arr[1]}</font></td>'
                    output += f'<td><font size=3 color=black>{arr[2]}</font></td>'
                    
                    if arr[7] == 'Fresh Sale':
                        output += f'<td><font size=3 color=black>{arr[3]}</font></td>'
                    else:
                        price = float(arr[3])
                        price = (price / 100) * 80
                        output += f'<td><font size=3 color=black>{price}</font></td>'
                    
                    output += f'<td><font size=3 color=black>{arr[4]}</font></td>'
                    output += f'<td><font size=3 color=black>{arr[5]}</font></td>'
                    
                    try:
                        # Using the correct method `get()` to retrieve the file from IPFS
                        content = api.get(arr[6])  # arr[6] is expected to be the IPFS hash
                        if content:
                            content = content['Content']  # Extract the content from the response
                            
                            # Remove the existing product image if it exists
                            if os.path.exists('EcommerceApp/static/product.jpg'):
                                os.remove('EcommerceApp/static/product.jpg')
                            
                            # Write the image content to a file
                            with open('EcommerceApp/static/product.jpg', "wb") as file:
                                file.write(content)
                            file.close()
                            
                            output += f'<td><img src="/static/product.jpg" width="200" height="200"></img></td>'
                        else:
                            output += '<td><font size=3 color=black>No image available</font></td>'
                    except Exception as e:
                        output += f'<td><font size=3 color=black>Error loading image</font></td>'
                        print(f"Error retrieving image from IPFS: {e}")

                    output += f'<td><font size=3 color=black>{arr[7]}</font></td>'
                    output += f'<td><a href=\'BookOrder?farmer={arr[1]}&crop={arr[2]}&t3={arr[7]}\'><font size=3 color=black>Click Here</font></a></td></tr>'
        
        output += "</table><br/><br/><br/><br/><br/><br/>"
        context = {'data': output}
        return render(request, 'SearchProducts.html', context)

        
    
def QuantityUpdateAction(request):
    if request.method == 'POST':
        pname = request.POST.get('t1', False)
        qty = request.POST.get('t2', False)
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        index = 0
        record = ''
        readDetails("addproduct")
        rows = details.split("\n")
        tot_qty = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "addproduct":
                if arr[1] == user and arr[2] == pname and arr[7] == 'Fresh Sale':
                    tot_qty = int(arr[4])
                    tot_qty = tot_qty + int(qty)
                    index = i
                    record = arr[0]+"#"+arr[1]+"#"+arr[2]+"#"+arr[3]+"#"+str(tot_qty)+"#"+arr[5]+"#"+arr[6]+"#"+arr[7]+"\n"
                    break
        for i in range(len(rows)-1):
            if i != index:
                record += rows[i]+"\n"
        updateQuantityBlock(record)
        context= {'data':"Quantity details updated & new available quantity: "+str(tot_qty)}
        return render(request, 'SupplierScreen.html', context)
          
                    
      

# def AddProductAction(request):
#     if request.method == 'POST':
#         cname = request.POST.get('t1', False)
#         qty = request.POST.get('t2', False)
#         price = request.POST.get('t3', False)
#         desc = request.POST.get('t4', False)
#         image = request.FILES['t5'].read()
#         imagename = request.FILES['t5'].name
#         user = ''
#         with open("session.txt", "r") as file:
#             for line in file:
#                 user = line.strip('\n')
#         file.close()
#         myfile = pickle.dumps(image)
#         hashcode = api.add_pyobj(myfile)
#         data = "addproduct#"+user+"#"+cname+"#"+price+"#"+qty+"#"+desc+"#"+hashcode+"#Fresh Sale\n"
#         saveDataBlockChain(data,"addproduct")
#         context= {'data':"Product details saved and IPFS image storage hashcode = "+hashcode}
#         return render(request, 'AddProduct.html', context)


import ipfshttpclient
import json

# Connect to the local IPFS daemon
api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

def AddProductAction(request):
    if request.method == 'POST':
        # Get form data
        cname = request.POST.get('t1', False)
        qty = request.POST.get('t2', False)
        price = request.POST.get('t3', False)
        desc = request.POST.get('t4', False)

        # Get image data from the uploaded file
        image = request.FILES['t5']
        imagename = image.name

        # Retrieve the user from the session (assuming session.txt stores the current user)
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()

        # Now handle the image upload to IPFS
        try:
            # Add image to IPFS (open the image in binary mode)
            result = api.add(image)
            print(result)  # You can remove this after testing

            # Get the IPFS hash of the image
            hashcode = result['Hash']

            # Prepare the product data to be stored on the blockchain
            data = "addproduct#"+user+"#"+cname+"#"+price+"#"+qty+"#"+desc+"#"+hashcode+"#Fresh Sale\n"

            # Call your function to save the data on the blockchain
            saveDataBlockChain(data, "addproduct")

            # Return success message with the IPFS hash of the image
            context = {'data': "Product details saved and IPFS image storage hashcode = " + hashcode}
            return render(request, 'AddProduct.html', context)
        
        except Exception as e:
            # Handle any error that occurs during the upload or blockchain saving process
            print(f"Error uploading file to IPFS: {e}")
            context = {'data': "Error uploading product. Please try again."}
            return render(request, 'AddProduct.html', context)



   
def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        usertype = request.POST.get('type', False)
        record = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "signup#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+usertype+"\n"
            saveDataBlockChain(data,"signup")
            context= {'data':'Signup process completd and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)    



def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        usertype = request.POST.get('type', False)
        status = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username and arr[2] == password and arr[6] == usertype:
                    status = 'success'
                    break
        if status == 'success' and usertype == 'Supplier':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'SupplierScreen.html', context)
        elif status == 'success' and usertype == 'Consumer':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'ConsumerScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)            


        
        



        
            
