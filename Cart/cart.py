from Shop.models import Product, Profile

class Cart():
	def __init__(self, request):
		self.session = request.session
		# get request
		self.request = request
		# Get the current key if it exists
		cart = self.session.get('session_key')

		# if user is new, create one
		if 'session_key' not in request.session:
			cart = self.session['session_key'] = {}

		# Make Sure the cart works in all pages
		self.cart = cart

	def db_add(self, product, quantity):
		product_id = str(product)
		product_qty = str(quantity)
		if product_id in self.cart:
			pass
		else:
			#self.cart[product_id] = {'price': str(product.price), 'qty': int(product_qty)}
			self.cart[product_id] = int(product_qty)
		self.session.modified = True
		# deal with logged in user
		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# convert
			carty = str(self.cart)
			carty = carty.replace("\'","\"")
			# save to profile
			current_user.update(old_cart=str(carty))

	def add(self, product, quantity):

		product_id = str(product.id)
		product_qty = str(quantity)
		if product_id in self.cart:
			pass
		else:
			#self.cart[product_id] = {'price': str(product.price), 'qty': int(product_qty)}
			self.cart[product_id] = int(product_qty)
		self.session.modified = True
		# deal with logged in user
		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# convert
			carty = str(self.cart)
			carty = carty.replace("\'","\"")
			# save to profile
			current_user.update(old_cart=str(carty))

	def __len__(self):
		return len(self.cart)
	
	def get_prods(self):
		# get ids from cart
		product_ids = self.cart.keys()

		# use ids to lookup products in db model
		products = Product.objects.filter(id__in=product_ids)
		return products
	
	def get_quants(self):
		quantities = self.cart
		return quantities
	
	def update(self, product, quantity):
		product_id = str(product)
		product_qty = int(quantity)

		# get cart
		cart = self.cart

		# update dictionary/cart
		cart[product_id] = product_qty
		self.session.modified = True
		
		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# convert
			carty = str(self.cart)
			carty = carty.replace("\'","\"")
			# save to profile
			current_user.update(old_cart=str(carty))
		
		
		thing = self.cart
		
		return thing

	def delete(self, product):
		product_id = str(product)
		# delete from dict/cart
		if product_id in self.cart:
			del self.cart[product_id]
		self.session.modified = True

		if self.request.user.is_authenticated:
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# convert
			carty = str(self.cart)
			carty = carty.replace("\'","\"")
			# save to profile
			current_user.update(old_cart=str(carty))
	
	def cart_total(self):
		# get product ids
		product_ids = self.cart.keys()
		# lookup keys in the db model
		products = Product.objects.filter(id__in=product_ids)
		# get quantities
		quantities = self.cart
		total = 0
		for key, value in quantities.items():
			key = int(key)
			for product in products:
				if product.id == key: # type: ignore
					if product.sale:
						total = total + (product.sale_price * value)
					else:
						total = total + (product.price * value)
		return total