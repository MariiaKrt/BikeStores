#!/usr/bin/env python
# coding: utf-8

# # Bike Store Data Analysis
# #### Dataset Source: [Bike Store Sample Database on Kaggle](https://www.kaggle.com/dillonmyrick/bike-store-sample-database)
# #### Download data to your PC: [Excel files](https://drive.google.com/drive/folders/1-6G7FG1BzN4QS1AmbaREzX2zq-fgnxoH) 
# 

# In[1]:


# import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# import data
orders = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/orders.xlsx')
order_items = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/order_items.xlsx')
stores = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/stores.xlsx')
stocks = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/stocks.xlsx')
staffs = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/staffs.xlsx')
products = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/products.xlsx')
customers = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/customers.xlsx')
categories = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/categories.xlsx')
brands = pd.read_excel('https://github.com/MariiaKrt/BikeStores/raw/main/brands.xlsx')


# In[2]:


# print a sample of each table to get an overview of the data
print(orders.sample(5))
print(order_items.sample(5))
print(products.sample(5))
print(categories.sample(5))
print(brands.sample(5))
print(staffs.sample(5))
print(stores.sample(5))
print(customers.sample(5))


# In[3]:


# display information about the structure of each table
print(orders.info())
print('')
print(order_items.info())
print('')
print(products.info())
print('')
print(categories.info())
print('')
print(brands.info())
print('')
print(staffs.info())
print('')
print(stores.info())
print('')
print(customers.info())


# In[4]:


# check null values
print(orders.isnull().sum())
print('')
print(order_items.isnull().sum())
print('')
print(products.isnull().sum())
print('')
print(categories.isnull().sum())
print('')
print(brands.isnull().sum())
print('')
print(staffs.isnull().sum())
print('')
print(stores.isnull().sum())
print('')
print(customers.isnull().sum())


# In[5]:


# check the data consistency

# create an empty list to store the results
check = []

# the 'orders' table stores sales data
# the 'order_items,' 'customers,' 'staffs,' and 'stores' tables are dictionaries
# checking that all data from the sales table is present in the dictionaries
check.append(set(orders.order_id.unique()).issubset(set(order_items.order_id.unique()))) 
check.append(set(orders.customer_id.unique()).issubset(customers.customer_id.unique()))
check.append(set(orders.staff_id.unique()).issubset(set(staffs.staff_id.unique()))) 
check.append(set(orders.store_id.unique()).issubset(set(stores.store_id.unique()))) 

# check the data across the dictionaries are consistent
check.append(set(order_items.product_id.unique()).issubset(set(products.product_id.unique())))
check.append(sorted(list(categories.category_id.unique())) == sorted(list(products.category_id.unique())))
check.append(sorted(list(brands.brand_id.unique())) == sorted(list(products.brand_id.unique())))


# display the results
check


# In[6]:


# this report focuses on comparing completed sales for 2016 and 2017
# order statuses: 1 = Pending; 2 = Processing; 3 = Rejected; 4 = Completed
orders = orders[(orders.order_date < '2018-01-01') & (orders.order_status == 4)]
orders.head(10)


# #### Lets' see the overall performance of the Bike store in 2016 and 2017

# In[7]:


# create style for plots
def custom_style():
    sns.set(style="whitegrid", palette=['#61f4de', '#6e78ff'])

def custom_plot():
    sns.despine(left = True, right = True, bottom = True)
    plt.yticks([])
    plt.ylabel('')
    plt.xlabel('')

# calculate order prices with discounts, adding year and month columns
order_items['final_price'] = order_items['list_price'] * (1 - order_items['discount']) * order_items['quantity']
order_prices = order_items.groupby('order_id')['final_price'].sum().reset_index()
orders = orders.merge(order_prices, on = 'order_id', how = 'left')
orders['month'] = pd.DatetimeIndex(orders.order_date).month
orders['year'] = pd.DatetimeIndex(orders.order_date).year

#calculate total sales by years and % growth
sum_by_years = orders.groupby('year')['final_price'].sum().reset_index()
sum_by_years['final_price'] = round(sum_by_years['final_price'])
sum_by_years['amounts'] = 'Amounts'
sum_pivot = sum_by_years.pivot('amounts', 'year', 'final_price').reset_index(drop = True)
sum_pivot['growth'] = sum_pivot[2017] / sum_pivot[2016]
print(f"Growth in 2017 compared to 2016 is {float(sum_pivot.growth - 1):.2%}")

#create a barplot
custom_style()
sum_years = sns.barplot(x = 'year', y = 'final_price', data = sum_by_years, estimator = sum)
sum_years.bar_label(sum_years.containers[0], fmt = '%.0f', fontsize = 13)
custom_plot()
plt.show()


# In[8]:


#create a barplot to show monthly sales
plt.figure (figsize = (14,8))

def est (x):
    return sum(x)/1000


sales = sns.barplot(x = 'month', 
            y = 'final_price', 
            hue = 'year', 
            data = orders, 
            ci = None, 
            estimator = est)
custom_plot()
plt.legend(fontsize = 14, loc = 'upper right')
plt.ylabel('Sales (in thousands)')
sales.bar_label(sales.containers[0], fmt = '%.0f', fontsize = 9)
sales.bar_label(sales.containers[1], fmt = '%.0f', fontsize = 9)
plt.show()


# #### 2017 performed better compared to 2016.
# #### What contributes to the revenue growth? 
# 
# - new store are opened in 2017? 
# - more staff is hired?
# - more orders? 
# - higher Average Order Value (AOV)? If yes, why? 
#     - more items in orders or new more expensive brands?
#     - impact of discounts?

# #### Let's see the sales by stores and sales staff

# In[9]:


#sales by stores
orders_by_stores = orders.merge(stores, on = 'store_id')
orders_by_stores = orders_by_stores.groupby(['store_name', 'year'])['final_price'].sum().reset_index()
fig, axes = plt.subplots(1, 2,figsize = (16,6), sharex=True)

#create color palette
store_list = list(orders_by_stores.store_name.unique())
dcolors = {}
dcolors_list = ['#caff8a', '#3bf4fb', '#ffb7ff']
indx = 0

for store in store_list:
    dcolors[store] = dcolors_list[indx]
    indx += 1
dcolors

# create barplot
plot2016 = sns.barplot(x = 'final_price', 
                       y = 'store_name', 
                       data = orders_by_stores[orders_by_stores.year == 2016].sort_values(by = 'final_price', ascending = False), 
                       palette = dcolors,
                       estimator = sum, 
                       ci = None,
                       ax = axes[0])
axes[0].set_title('2016')
axes[0].set_ylabel('')
axes[0].set_xlabel('')
plot2016.bar_label(plot2016.containers[0], fmt='%.0f', fontsize = 13)

plot2017 = sns.barplot(x = 'final_price', 
                       y = 'store_name', 
                       data = orders_by_stores[orders_by_stores.year == 2017].sort_values(by = 'final_price', ascending = False), 
                       palette = dcolors,
                       estimator = sum,
                       ci = None,
                       ax = axes[1])
axes[1].set_title('2017')
axes[1].set_ylabel('')
axes[1].set_xlabel('')
plot2017.bar_label(plot2017.containers[0], fmt='%.0f', fontsize = 13)

plt.subplots_adjust(wspace=0.4)
plt.show()


# In[10]:


#sales by staff
staffs['name'] = staffs.first_name + ' ' + staffs.last_name
orders_by_staff = orders.merge(staffs, on = 'staff_id')
orders_by_staff = orders_by_staff.groupby(['name', 'year'])['final_price'].sum().reset_index()
fig, axes = plt.subplots(1, 2,figsize = (16,10), sharex=True)

# create color palette
staffs_list = list(orders_by_staff.name.unique())
scolors = {}
colors_list = ['#9b5de5', '#ff99c8', '#e4c1f9', '#00bbf9', '#d9d9d9', '#00f5d4']
ind = 0

for staff in staffs_list:
    scolors[staff] = colors_list[ind]
    ind += 1
scolors
   
#create barplot
plot2016 = sns.barplot(x = 'final_price', 
                       y = 'name', 
                       data = orders_by_staff[orders_by_staff.year == 2016].sort_values(by='final_price', ascending = False), 
                       estimator = sum, 
                       ci = None,
                       palette = scolors,
                       ax = axes[0])
axes[0].set_title('2016')
axes[0].set_ylabel('')
axes[0].set_xlabel('')
plot2016.bar_label(plot2016.containers[0], fmt='%.0f', fontsize = 13)

plot2017 = sns.barplot(x = 'final_price', 
                       y = 'name', 
                       data = orders_by_staff[orders_by_staff.year == 2017].sort_values(by = 'final_price', ascending = False), 
                       estimator = sum,
                       ci = None,
                       palette = scolors,
                       ax = axes[1])
axes[1].set_title('2017')
axes[1].set_ylabel('')
axes[1].set_xlabel('')
plot2017.bar_label(plot2017.containers[0], fmt='%.0f', fontsize = 13)

plt.subplots_adjust(wspace=0.4)
plt.show()


# #### No new stores or sales team growth. But the sales has grown in 2 out of 3 stores. Let's see if the increased number of orders is the reason of the revenue growth.

# In[11]:


# calculate number of completed orders by years
orders_by_years = orders.groupby('year')['order_id'].nunique().reset_index()
orders_by_years['orders'] = 'Orders'
pivot_orders = orders_by_years.pivot('orders', 'year', 'order_id').reset_index(drop = True)
pivot_orders['growth'] = pivot_orders[2017] / pivot_orders[2016] - 1
print(f"Growth in 2017 compared to 2016 is {float(pivot_orders['growth']):.2%}")

# creat a barplot
orders_plot= sns.barplot(x = 'year', y = 'order_id', data = orders_by_years)
custom_plot()
orders_plot.bar_label(orders_plot.containers[0], fontsize = 13)
plt.show()


# In[12]:


#create a barplot to show the number of orders monthly
plt.figure(figsize = (14, 8))
order_count = sns.barplot(x = 'month',
                          y = 'order_id',
                          hue = 'year',
                          data = orders,
                          ci = None,
                          estimator = np.count_nonzero)
custom_plot()
order_count.bar_label(order_count.containers[0], fmt = '%.0f', fontsize = 12)
order_count.bar_label(order_count.containers[1], fmt = '%.0f', fontsize = 12)
plt.ylabel('Number of orders')
plt.legend(loc = 'upper right', fontsize = 14)
plt.show()


# #### There doesn't seems to be the same growth in the number of orders. Let's check the AOV of 2016 and 2017.

# In[13]:


# calculate AOV for 2016 and 2017
aov_by_years = orders.groupby('year')['final_price'].mean().reset_index()
aov_growth = aov_by_years[aov_by_years.year == 2017].final_price.sum() / aov_by_years[aov_by_years.year == 2016].final_price.sum() 
print(f"The AOV growth in 2017 compared to 2016 is {float(aov_growth - 1):.2%}")

# create a barplot
aov_chart = sns.barplot(x = 'year', y = 'final_price', data = aov_by_years)
custom_plot()
aov_chart.bar_label(aov_chart.containers[0], fmt = '%.0f', fontsize = 12)
plt.show()


# In[14]:


#what's the distribution of order amounts?
plt.figure(figsize = (13, 7))
sns.boxplot(x = 'year', y = 'final_price', data = orders)
plt.xlabel('')
plt.ylabel('Order price')
plt.show()


# #### In 2017, there is an increase in orders with higher costs compared to 2016. Why? More items per order, changes in store discount policy, or the introduction of more expensive brands?
# #### First let's check if the number of items in the order has grown.

# In[15]:


# calculate the average number of items per order in 2016 and 2017
number_of_items = order_items.groupby('order_id')['quantity'].sum().reset_index()
orders_w_quantity = number_of_items.merge(orders, on = 'order_id')
av_quantity = orders_w_quantity.groupby('year')['quantity'].mean().reset_index()
dif = av_quantity[av_quantity.year == 2017].quantity.sum() / av_quantity[av_quantity.year == 2016].quantity.sum() -1
print(f"Growth in 2017 compared to 2016 is {float(dif):.2%}")

# create a barplot
qty_plot = sns.barplot(x = 'year', y = 'quantity', data = av_quantity)
custom_plot()
qty_plot.bar_label(qty_plot.containers[0], fmt = '%.3f', fontsize = 12) 
plt.show()


# #### There's a small increase in the number of items, but it's not enouth to be the main reason for the 41% revenue growth in 2017. Let's explore further. Has the discount policy changed?

# In[16]:


# calculate the average discount and the total discount amount yearly
order_items['price_no_discount'] = order_items['list_price'] * order_items['quantity']
order_prices_no_disc = order_items.groupby('order_id')['price_no_discount'].sum().reset_index()
orders = orders.merge(order_prices_no_disc, on = 'order_id', how = 'left')
orders['difference'] = orders['price_no_discount'] - orders['final_price']
orders['discount_by_orders'] = orders['difference'] / orders['price_no_discount']

av_discount = orders.groupby('year')['discount_by_orders'].mean().reset_index()
av_discount['discount_by_orders'] = round(av_discount['discount_by_orders'] * 100, 2)

sum_discount_amount = orders.groupby('year')['difference'].sum().reset_index()
sum_discount_amount['difference'] = round(sum_discount_amount['difference'])

discount_merged = av_discount.merge(sum_discount_amount, on = 'year')
discount_merged.rename(columns = {'discount_by_orders': 'discount, %','difference': 'discount amount'}, inplace = True)
discount_merged


# #### The average discount in 2017 is almost the same as in 2016. Let's look at the products. What products were sold in 2016, and how does it compare to 2017?

# In[17]:


# merge product and category names to the 'orders' table
products_all = order_items[['product_id', 'order_id','list_price', 'final_price']].merge(orders[orders.order_status == 4][['order_id', 'order_date','month' ,'year']], on = 'order_id')
products_names = products_all.merge(products, on = 'product_id').merge(categories, on = 'category_id')

# calculate average product price by years
product_price = products_all.groupby('year')['final_price'].mean().reset_index()
product_price['final_price'] = round(product_price['final_price'])
av_product_price = product_price[product_price['year'] == 2017].final_price.sum() / product_price[product_price['year'] == 2016].final_price.sum()
print(f"The average product price growth in 2017 compared to 2016 is {float(av_product_price - 1):.2%}")

# create a boxplot with product prices by years
plt.figure(figsize = (13, 7))
sns.boxplot(x = 'year', y = 'final_price', data = products_names)
plt.xlabel('')
plt.ylabel('Product price')
plt.show()


# ##### There are many more expensisive products in 2017.

# In[18]:


plt.figure(figsize = (16,8))
sns.boxplot(x = 'category_name', y = 'final_price', data = products_names, hue = 'year')
plt.xlabel('')
plt.ylabel('Product price')
plt.show()


# #### The mean is higher in most categories for 2017, and the most expensive products in each category also cost more in 2017. There is a new category with the highest product prices in 2017.

# #### With consistent resources  - the same sales team size, the same discount policy, and almost the same order volume— the Bike store grew revenue by selling higher-priced products and introducing new more expensive categories.
