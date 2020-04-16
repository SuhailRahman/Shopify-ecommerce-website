from flask import Flask, render_template, request,jsonify,abort,url_for,redirect
from flask_mysqldb import MySQL
import json
import datetime
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ecom'

mysql = MySQL(app)

@app.route("/get_image",methods=["GET"])
def get_image():
	return render_template("image.txt")

@app.route("/index",methods=["GET"])
def index():
	if request.method == 'GET':
		name= request.args['name']
		cur = mysql.connection.cursor()
		sql="select count(*) from cart where customer_id=%s"
		with open('cust_id.json') as f:
					data=json.load(f)
		customer_id=data['customer_id']
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		cart_no=rv[0][0]
		cur.execute('''SELECT * FROM product''')
		rv = cur.fetchall()
		sql="select p.image1,p.name,p.price,o.product_id,p.description,count(*) from orders o inner join product p on o.product_id=p.product_id group by o.product_id "
		cur.execute(sql)
		top_prod = cur.fetchall()
		top_products=sorted(top_prod, key = lambda x: x[5])
		cur.close()
		a="""<img class="borderedbox inspace-10" """
		w=""" src="{{url_for('static', filename='img/"""
		b= top_products[-1][0]
		c="""')}}" style="border:none">; """
		d=top_products[-1][1]
		e=";"
		f=top_products[-1][-2]
		i=";"
		q=a+w+b+c+d+e+f+i
		f = open("Templates/image.txt", "w")
		f.write(q)
		f.close()
		if(len(top_products)==0):
			return render_template('index.html', product=rv,name=name,top_products=1,cart_no=cart_no)
		else:
			return render_template('index.html', product=rv,name=name,top_products=top_products[-1],cart_no=cart_no)



@app.route("/product1",methods=["GET"])
def product1():
	if request.method == 'GET':
		cur = mysql.connection.cursor()
		productId=request.args.get('productId')
		sql="select count(*) from cart where customer_id=%s"
		with open('cust_id.json') as f:
			data=json.load(f)
		customer_id=data['customer_id']
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		cart_no=rv[0][0]
		sql="select name from users where user_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		name=cur.fetchall()
		sql="select distinct name,image1, description, price, product_id from (select p.name as name,p.image1 as image1,p.description as description,p.price as price,p.product_id as product_id from product p inner join orders o on o.product_id=p.product_id where o.customer_id=%s order by o.cur_date DESC ) as table1 LIMIT 3"
		val=(str(customer_id),)
		cur.execute(sql,val)
		o_prod=cur.fetchall()
		#return jsonify(o_prod)
		length=len(o_prod)
		sql="select category from product where product_id=%s"
		val=(str(productId),)
		cur.execute(sql,val)
		category=cur.fetchall()
		#return jsonify(category)
		limit=6-length
		sql="select name,image1,description,price,product_id from product where category=%s and product_id<>%s LIMIT %s"
		val=(str(category[0][0]),str(productId),limit)
		cur.execute(sql,val)
		r_prod=cur.fetchall()
		#return jsonify(r_prod)
		recom_product=[]
		for i in o_prod:
			recom_product.append(i)
		for i in r_prod:
			recom_product.append(i)
		cur.execute('''SELECT * FROM product''')
		rv = cur.fetchall()
		cur.close()
		for i in rv:
			if(productId == str(i[0])):
				return render_template('product1.html',recom_product=recom_product,id=i[0],name=name[0][0],description=i[3],category=i[4],pname=i[1],price=i[2],image1=i[-4],image2=i[-3],image3=i[-2],image4=i[-1],cart_no=cart_no)

@app.route("/register",methods=["GET","POST"])
def register():
	if request.method == 'POST':
        #Parse form data  

		name = request.form['name']
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		address = request.form['address']
		contact = request.form['contact']
		if(name=="" or username=="" or password=="" or email=="" or address=="" or contact==""):
			return render_template('signup.html',flag=1)
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO users (name, username, password, email, address, contact) VALUES ( %s, %s, %s, %s, %s, %s)', [name,username,password,email,address,contact])
		mysql.connection.commit()
		cur.close()
	return render_template('login.html')


@app.route("/signup",methods=["GET","POST"])
def signup():
	return render_template('signup.html',flag=0)


@app.route("/login_page", methods = ['POST','GET'])
def login_page():

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['pass']
		cur = mysql.connection.cursor()
		cur.execute('''SELECT * FROM users''')
		rv = cur.fetchall()
		cur.close()
		for i in rv:
			if(i[4]==email and i[3]==password):
				a=i[0]
				with open('cust_id.json') as f:
					data=json.load(f)
				data['customer_id']=a
				with open('cust_id.json','w') as json_file:
					json.dump(data,json_file)
				return redirect(url_for('index',name=i[1]))
	return render_template('login.html',flag=1)


@app.route("/",methods=["GET","POST"])
def login():
	return render_template('login.html',flag=0)

@app.route("/cart_details",methods=["GET"])
def cart_details():
	if request.method == 'GET':
		cur = mysql.connection.cursor()
		with open('cust_id.json') as f:
					data=json.load(f)
		customer_id=data['customer_id']
		sql="select count(*) from cart where customer_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		cart_no=rv[0][0]
		sql="select name from users where user_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		name=cur.fetchall()
		sql="select p.image1,p.name,c.rate,c.quantity,c.price from cart c inner join product p on p.product_id=c.product_id  where c.customer_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		cur.close()
		total=0
		for i in rv:
			total+=i[4]
		return render_template('shopping-cart.html',cart_no=cart_no,product=rv,total=total,name=name[0])
	abort(404)

@app.route("/order_placed",methods=["POST"])
def order_placed():
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		with open('cust_id.json') as f:
					data=json.load(f)
		customer_id=data['customer_id']
		sql="select name from users where user_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		name=cur.fetchall()
		sql="select * from cart where customer_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		cart=cur.fetchall()
		list_cart=len(cart)
		sql = "INSERT INTO orders (customer_id,product_id,rate,qty,amount) VALUES (%s,%s,%s,%s,%s)"
		for i in cart:
			val = (str(customer_id),i[0],i[2],i[3],i[4])
			cur.execute(sql,val)
			mysql.connection.commit()
		cart=cur.fetchall()	
		sql="select order_id from orders where customer_id=%s order by order_id DESC LIMIT 1"
		val=(str(customer_id),)
		cur.execute(sql,val)
		temp_last_order_id=cur.fetchall()
		o_id=int(temp_last_order_id[0][0])-list_cart
		o_id_list=[]
		sql = "INSERT INTO tracking_orders (order_id) VALUES (%s)"
		for i in range(list_cart):
			o_id=int(o_id)+1
			val = (str(o_id),)
			cur.execute(sql,val)
			mysql.connection.commit()
			o_id_list.append(o_id)
		sql = "DELETE FROM CART where customer_id=(%s)"	
		val=(str(customer_id),)
		cur.execute(sql,val)
		mysql.connection.commit()
		cur.close()
		return redirect(url_for("track_order"))
	abort(404)
	
@app.route("/add_to_cart",methods=["POST"])
def add_to_cart():
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		productId=request.args.get('productId')
		with open('cust_id.json') as f:
					data=json.load(f)
		customer_id=data['customer_id']
		sql='''SELECT * FROM product where product_id= %s'''
		val=(str(productId),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		l=rv[0]
		quantity=request.form['quantity']
		sql = "INSERT INTO cart (product_id,customer_id,rate,quantity,price) VALUES (%s,%s,%s,%s,%s)"
		val = (str(l[0]), str(customer_id),str(l[2]),str(quantity),str(l[2]*int(quantity)))
		cur.execute(sql,val)
		mysql.connection.commit()
		cur.close()
		return redirect(url_for("product1",productId=productId))


@app.route("/track_order",methods=["GET"])
def track_order():
	if request.method == 'GET':
		cur = mysql.connection.cursor()
		with open('cust_id.json') as f:
					data=json.load(f)
		customer_id=data['customer_id']
		sql="select count(*) from cart where customer_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		cart_no=rv[0][0]
		sql="select name from users where user_id=%s"
		val=(str(customer_id),)
		cur.execute(sql,val)
		name=cur.fetchall()
		sql='''SELECT o.product_id,t.order_id,t.status FROM tracking_orders t inner join orders o ON o.order_id=t.order_id where o.customer_id= %s'''
		val=(str(customer_id),)
		cur.execute(sql,val)
		rv = cur.fetchall()
		list_products=[]
		for i in rv:
			l=[]
			sql='''SELECT image1,name FROM product where product_id= %s'''
			val=(str(i[0]),)
			cur.execute(sql,val)
			r = cur.fetchall()
			l.extend(i)
			l.extend(r[0])
			list_products.append(l)
		cur.close()
		return render_template("tracking_orders.html",cart_no=cart_no,product=list_products,name=name[0])

if __name__ == '__main__':
    app.run()