#!/usr/bin/env python
# coding: utf-8

# # Рынок заведений общественного питания Москвы

# **Описание проекта**
# 
# Инвесторы из фонда «Shut Up and Take My Money» решили попробовать себя в новой области и открыть заведение общественного питания в Москве. Заказчики ещё не знают, что это будет за место: кафе, ресторан, пиццерия, паб или бар, — и какими будут расположение, меню и цены.
# 
# Для начала они просят вас — аналитика — подготовить исследование рынка Москвы, найти интересные особенности и презентовать полученные результаты, которые в будущем помогут в выборе подходящего инвесторам места.
# Постарайтесь сделать презентацию информативной и лаконичной. Её структура и оформление сильно влияют на восприятие информации читателями вашего исследования. Выбирать инструменты (matplotlib, seaborn и другие) и типы визуализаций вы можете самостоятельно.
# 
# Вам доступен датасет с заведениями общественного питания Москвы, составленный на основе данных сервисов Яндекс Карты и Яндекс Бизнес на лето 2022 года. Информация, размещённая в сервисе Яндекс Бизнес, могла быть добавлена пользователями или найдена в общедоступных источниках. Она носит исключительно справочный характер.

# **Описание данных**
# 
# *Файл moscow_places.csv:*
# - name — название заведения;
# - address — адрес заведения;
# - category — категория заведения, например «кафе», «пиццерия» или «кофейня»;
# - hours — информация о днях и часах работы;
# - lat — широта географической точки, в которой находится заведение;
# - lng — долгота географической точки, в которой находится заведение;
# - rating — рейтинг заведения по оценкам пользователей в Яндекс Картах (высшая оценка — 5.0);
# - price — категория цен в заведении, например «средние», «ниже среднего», «выше среднего» и так далее;
# - avg_bill — строка, которая хранит среднюю стоимость заказа в виде диапазона, например:
#     * «Средний счёт: 1000–1500 ₽»;
#     * «Цена чашки капучино: 130–220 ₽»;
#     * «Цена бокала пива: 400–600 ₽» и так далее;
# - middle_avg_bill — число с оценкой среднего чека, которое указано только для значений из столбца avg_bill, начинающихся с подстроки «Средний счёт»:
#     * Если в строке указан ценовой диапазон из двух значений, в столбец войдёт медиана этих двух значений.
#     * Если в строке указано одно число — цена без диапазона, то в столбец войдёт это число.
#     * Если значения нет или оно не начинается с подстроки «Средний счёт», то в столбец ничего не войдёт.
# - middle_coffee_cup — число с оценкой одной чашки капучино, которое указано только для значений из столбца avg_bill, начинающихся с подстроки «Цена одной чашки капучино»:
#     * Если в строке указан ценовой диапазон из двух значений, в столбец войдёт медиана этих двух значений.
#     * Если в строке указано одно число — цена без диапазона, то в столбец войдёт это число.
#     * Если значения нет или оно не начинается с подстроки «Цена одной чашки капучино», то в столбец ничего не войдёт.
# - chain — число, выраженное 0 или 1, которое показывает, является ли заведение сетевым (для маленьких сетей могут встречаться ошибки):
#     * 0 — заведение не является сетевым
#     * 1 — заведение является сетевым
# - district — административный район, в котором находится заведение, например Центральный административный округ;
# - seats — количество посадочных мест.

# In[1]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from plotly import graph_objects as go
import plotly.express as px
from folium import Map, Choropleth
from folium import Marker, Map
from folium.plugins import MarkerCluster


# ### Загрузка данных и изучение общей информации

# In[2]:


df = pd.read_csv('/datasets/moscow_places.csv')


# In[3]:


df.head(5)


# In[4]:


df.info()


# Что касается типа данных, то все они представлены либо в object, либо в float64, один стоблец имеет тип - int.

# In[5]:


print('Всего уникальных заведений', df['name'].nunique())


# In[6]:


df['category'].unique()


# 8 уникальных категорий заведений.

# In[7]:


df.isna().sum()


# Есть пропуски в следующих столбцах:'hours', 'price', 'avg_bill', 'middle_avg_bill', 'middle_coffee_cup' и 'seats'.

# ### Предобработка данных

# **Явные и неявные дубликаты**

# Изучим данные на наличие явных дубликатов. Спойлер: их нет.

# In[8]:


df.duplicated().sum()


# Посмотрим есть ли неявные дубликаты по адресу и названию заведения.

# In[9]:


df_1 = df['name'] + df['address']
df_1


# Приведем данные к нижнему регистру.

# In[10]:


df_1 = df_1.str.lower()
df_1.duplicated().sum()


# In[11]:


df_1[df_1.duplicated()]


# In[12]:


df = df.drop(index=[215, 1511, 2420, 3109])


# **Пропуски**

# Пропуски в столбцах 'hours', 'price', 'avg_bill', 'seats' оставляем. А 'middle_avg_bill', 'middle_coffee_cup' изучим по 'avg_bill'.

# In[13]:


#df['avg_bill'].unique()


# In[14]:


df[(df['middle_avg_bill'].isnull()) & (df['avg_bill'] == 'Средний счёт%')]


# In[15]:


df[(df['middle_coffee_cup'].isnull()) & (df['avg_bill'] == 'Цена чашки%')]


# Нет таких строк, где бы столбец 'avg_bill' был заполнен, а среднее по нему в столбцах 'middle_avg_bill' или 'middle_coffee_cup' нет =>  'middle_avg_bill', 'middle_coffee_cup' никак не заполняем.

# *Итог:* пропуски не трогаем.

# Создадим **столбец street** с названиями улиц из столбца с адресом.

# In[16]:


df['street'] = df['address'].str.split(', ').str[1]
df['street']


# Создадим **столбец is_24/7** с обозначением, что заведение работает ежедневно и круглосуточно (24/7):
# - логическое значение True — если заведение работает ежедневно и круглосуточно;
# - логическое значение False — в противоположном случае.

# In[17]:


df['is_24/7'] = df['hours'].str.contains('ежедневно, круглосуточно', case=False, na=False)


# In[18]:


df


# ### Анализ данных

# **Количество объектов общественного питания по категориям** 

# Для начала посмотрим количество заведений по категориям.

# In[19]:


number_of_objects = df.groupby('category')['name'].agg({'count'}).sort_values('count', ascending=False).reset_index()
number_of_objects


# In[20]:


sns.set_style('whitegrid')
plt.figure(figsize=(10, 7))
plt.title('Количество объектов общественного питания по категориям')
plt.xticks(rotation=20) 
sns.barplot(x='category', y='count', data=number_of_objects, color='lightblue')
plt.xlabel('Категория')
plt.ylabel('Количество заведений')
plt.show()


# По графику видно, что больше всего заведений по категории 'кафе'. Также много ресторанов и кофейнь в данных, а меньше всего булочных.

# Теперь посмотрим на **распределение заведений по категориям** с помощью круговой диаграммы.

# In[21]:


number_of_objects['share'] = round(number_of_objects['count'] / number_of_objects['count'].sum() * 100, 3)
number_of_objects


# In[22]:


name = ['Кафе', 'Ресторан', 'Кофейня', 'Бар, паб', 'Пиццерия', 'Быстрое питание', 'Столовая', 'Булочная']
fig_1 = go.Figure(data=[go.Pie(labels=name,
                             values=number_of_objects['share'], 
                             pull = [0.1, 0])])
fig_1.update_layout(title='Распределение заведений по категориям')
fig_1.show()


# Большую долю на рынке занимают кафе(28,3%), около 1/4 (24,3%) - рестораны и почти 17% - кофейни. Меньше 5% рынка занимают столовые, а также булочные.

# **Количество посадочных мест в местах по категориям**

# Для более точного анализа посчитаем медиану посадочных мест по категориям, поскольку на количество посадочных мест в сумме влияет количество заведений.

# In[23]:


median_of_seats = df.groupby('category')['seats'].agg({'median'}).sort_values('median', ascending=False).reset_index()
median_of_seats['median'] = round(median_of_seats['median'], 3)
median_of_seats['share'] = round(median_of_seats['median'] / median_of_seats['median'].sum() * 100, 3)
median_of_seats


# In[24]:


sns.set_style('whitegrid')
plt.figure(figsize=(10,5))
plt.xticks(rotation=20) 
sns.barplot(data=median_of_seats, x='category', y='median', color='lightblue')
plt.title('Медианное количество посадочных мест по категориям')
plt.ylabel('Количество мест')
plt.xlabel('Категория')
plt.show()


# На данном графике видно, что больше всего посадочных мест в барах, пабах, ресторанах и кофейнях.

# In[25]:


name = ['Ресторан', 'Бар, паб', 'Кофейня', 'Столовая', 'Быстрое питание', 'Кафе', 'Пиццерия', 'Булочная']
fig_2 = go.Figure(data=[go.Pie(labels=name,
                             values=median_of_seats['share'], 
                             pull = [0.1, 0])])
fig_2.update_layout(title='Распределение посадочных мест по категориям')
fig_2.show()


# От всего количества посадочных мест 15.5% составляют рестораны, 14.8% - бары, пабы, 14.5% - кофейни.

# **Соотношение сетевых и несетевых заведений** 

# In[26]:


chain = df['chain'].value_counts().reset_index()
chain


# Посмотрим на соотношение сетевых и несетевых заведений с помощью круговой диаграммы.

# In[27]:


chain['share'] = round(chain['chain'] / chain['chain'].sum() * 100, 3)
chain


# In[28]:


name = ['Не сеть', 'Сеть']
fig_3 = go.Figure(data=[go.Pie(labels=name,
                             values=chain['share'], 
                             pull = [0.1, 0])])
fig_3.update_layout(title='Соотношение сетевых и несетевых заведений')
fig_3.show()


# Практически 62% заведений не являются сетевыми.

# **Распределение сетевых заведенй по категорям**

# Чтобы понять, какие категории заведений чаще являются сетевыми, посчитаем процент сетевых от общего количества заведений каждого типа.

# In[29]:


chain_yes = df[df['chain'] == 1]
chain_yes_1 = chain_yes.groupby('category')['name'].agg({'count'}).sort_values('count', ascending=False).reset_index()
chain_yes_1


# In[30]:


category_chain = pd.merge(number_of_objects, chain_yes_1, how='left', on='category')
category_chain = category_chain.drop('share', axis=1)
category_chain = category_chain.rename(columns={'count_x': 'all_count', 'count_y': 'chain_count'})
category_chain['share'] = round(category_chain['chain_count'] / category_chain['all_count'] * 100, 3)
category_chain = category_chain.sort_values('share', ascending=False)
category_chain


# Видно, что больше всего сетевых заведений среди булочных, пиццерий и кофейнь.

# In[31]:


sns.set_style('whitegrid')
plt.figure(figsize=(10,5))
plt.xticks(rotation=20) 
sns.barplot(data=category_chain, x='category', y='share', color='lightblue')
plt.title('Распределение сетевых заведенй по категорям')
plt.ylabel('Процент сетевых от общего количества заведений')
plt.xlabel('Категория')
plt.show()


# В категории "булочная" 61.3% занимают сети, в категории "пиццерия" - 52.1%, в "кофейнях" - 51%. А в категории "столовая" это значение равняется 28%, в категории "бар, паб" - 22%.

# **Топ-15 популярных сетей в Москве** 

# Для начала приведем все названия к нижнему регистру.

# In[32]:


df['name'] = df['name'].str.lower()


# In[33]:


popular_chain_yes = df[df['chain'] == 1].groupby('name')['name'].agg({'count'}).sort_values('count', ascending=False).reset_index().head(15)
popular_chain_yes


# Теперь построим визуализацию.

# In[34]:


sns.set_style('whitegrid')
plt.figure(figsize=(10, 7))
plt.title('Топ-15 популярных сетей в Москве')
sns.barplot(x='count', y='name', data=popular_chain_yes, palette=("pastel"))
plt.xlabel('Количество заведений')
plt.ylabel(' ')
plt.show()


# Шоколадница, Домино'с пицца, Додо пицца, One price coffee, Яндекс лавка, Cofix - лидеры среди сетевых общепитов.

# Теперь посмотрим, к каким категориям относятся данные заведения.

# In[35]:


popular_chain_categories = df.query('name in @popular_chain_yes.name').pivot_table(index='name', values='address', columns='category', aggfunc='count', margins=True).sort_values('All', ascending=False)
popular_chain_categories = popular_chain_categories.drop('All', axis = 0)
popular_chain_categories


# In[36]:


popular_chain_categories.sort_values('All', ascending=True).drop(['All'], axis=1).plot(kind='barh', stacked=True, figsize=(10,7))
plt.title('Топ-15 популярных сетей в Москве по категориям')
plt.xlabel('Количество заведений')
plt.ylabel(' ')
plt.show()


# Топовые общепиты - общепиты категории кофейня, пиццерия и ресторан. Из интересного: Му-му, Чайхона, Хинкальная и Буханка состоят из трех и больше типов категорий. Кофейнями практически полностью являются Cofefest, Кофепорт, Cofix, One Price Coffee и Шоколадница. Ресторанами являются Теремок, Prime и Яндекс Лавка. Пиццерии - Додо Пицца и Домино'с Пицца, а кафе - Кулинарная лавка братьев Караваевых.

# **Общее количество заведений и количество заведений каждой категории по районам**

# In[37]:


df_district = df.groupby('district')['name'].agg({'count'})
df_district


# Для удобного восприятия информации построим визуализацию.

# In[38]:


df_district_pivot = df.pivot_table(index='district', values='name', columns='category', aggfunc='count', margins=True).sort_values('All', ascending=False).reset_index()
df_district_pivot = df_district_pivot.drop(index=0)
df_district_pivot


# In[39]:


fig_4 = px.bar(df_district_pivot, x="district", y=["бар,паб",
                                                   "булочная",
                                                   "быстрое питание",
                                                   "кафе", "кофейня",
                                                   "пиццерия",
                                                   "ресторан",
                                                   "столовая"], 
               title="Количество заведений каждой категории по районам",
              labels=dict(district=' ', value='Количество', variable='Категория'))
fig_4.update_layout(
    autosize=False,
    width=900,
    height=600)
fig_4.show()


# Вывод: по графику видно, что во всех округах преобладают категории "кафе", "ресторан" и "кофейня". А в ЦАО также много баров, пабов. Меньше всего заведений с такой категорией, как "булочная" и "столовая".  

# **Распределение средних рейтингов по категориям заведений**

# In[40]:


ratings = df.groupby('category')['rating'].agg({'mean'}).sort_values('mean', ascending=False).reset_index()
ratings['mean'] = round(ratings['mean'], 3)
ratings


# In[41]:


fig_5 = px.bar(ratings, x='category', y='mean', labels=dict(category=' ', mean='Рейтинг'),
               title='Распределение средних рейтингов по категориям заведений',
              color_discrete_sequence=['lightblue'])
fig_5.update_layout(
    autosize=False,
    width=700,
    height=500,
    yaxis_range=[3.5, 5])
fig_5.show()


# Построив график, можно увидеть, что средняя оценка по категориям несильно различается. Однако самый высокий рейтинг в барах, пабах - 4.38, и низкий рейтинг - в кафе(4.12) и быстром питании(4.05).

# **Фоновая картограмма (хороплет) со средним рейтингом заведений каждого района**

# Для каждого округа посчитаем средний рейтинг заведений, которые находятся на его территории.

# In[42]:


rating_df = df.groupby('district', as_index=False)['rating'].agg('mean').sort_values('rating', ascending=False)
rating_df['rating'] = round(rating_df['rating'], 3)
rating_df


# In[43]:


state_geo = '/datasets/admin_level_geomap.geojson'
moscow_lat, moscow_lng = 55.751244, 37.618423


# In[44]:


m_1 = Map(location=[moscow_lat, moscow_lng], zoom_start=10)


# In[45]:


Choropleth(
    geo_data=state_geo,
    data=rating_df,
    columns=['district', 'rating'],
    key_on='feature.name',
    fill_color='YlGn',
    fill_opacity=0.8,
    legend_name='Средний рейтинг заведений по округам',
).add_to(m_1)
m_1


# Самый высокий средний рейтинг - в ЦАО, чуть ниже - в САО, СЗАО. Ниже всего - в ЮВАО.

# **Все заведения датасета на карте с помощью кластеров средствами библиотеки folium**

# In[46]:


m_2 = Map(location=[moscow_lat, moscow_lng], zoom_start=10)


# In[47]:


marker_cluster = MarkerCluster().add_to(m_2)

def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

df.apply(create_clusters, axis=1)

m_2


# По кластерам видно, что меньше всего заведений в ЮАО, ЮВАО, ВАО.

# **Улицы, на которых находится только один объект общепита**

# In[48]:


one_object = df.pivot_table(index=['street'], values='name', aggfunc='count').reset_index().query('name == 1')
one_object


# In[49]:


one_object_by_district = df.pivot_table(index=['street', 'district'], values='name', aggfunc='count').reset_index().query('name == 1')
one_object_by_district


# Улица может находится одновременно в двух районах. Проверим, есть ли у нас такой случай в данных.

# In[50]:


one_object_by_district['street'].duplicated().sum()


# In[51]:


one_object_by_district[one_object_by_district['street'].duplicated()]


# In[52]:


one_object_by_district[one_object_by_district['street'] == 'улица Золоторожский Вал']


# Нашли! Есть одно заведение, на улице Золоторожский Вал, которое одновременно находится в двух районах по данным. НО! В реальности данная улица не может находится в двух этих районах хотя бы потому, что САО и ЮВАО - не соседи. Вывод: скорее всего здесь есть какая-то ошибка в самом названии улицы или же округа.
# 
# Посмотрим на информацию в таблице df.

# In[53]:


df[df['street'] == 'улица Золоторожский Вал']


# Посмотрев, в каком округе находится адрес кофейни you&coffee, выяснилось, что она находится на самом деле в ЮВАО. Упс, ошибочка!

# Сгруппируем данные по району и посмотрим в каких районах есть много улиц, на которых находится только один объект общепита.

# In[54]:


one_object_by_district_sum = one_object_by_district.groupby('district')['name'].count().to_frame().sort_values('name', ascending=False).reset_index()
one_object_by_district_sum


# In[55]:


sns.set_style('whitegrid')
plt.figure(figsize=(10, 7))
plt.title('Количество улиц с одним объектом общественного заведения по округам') 
sns.barplot(x='name', y='district', data=one_object_by_district_sum, color='lightblue')
plt.xlabel('Количество')
plt.ylabel(' ')
plt.show()


# Больше всего улиц с одним заведением в ЦАО, что интересно. В СВАО, втором округе по количеству таких улиц, значение меньше - в 2,5 раза. И меньше всего улиц с одним общепитом - в ЮЗАО.

# **Медианный чек заведений по округам**

# In[56]:


middle_avg_bill_district = df.groupby('district')['middle_avg_bill'].median().to_frame().sort_values('middle_avg_bill', ascending=False).reset_index()
middle_avg_bill_district


# In[57]:


m_3 = Map(location=[moscow_lat, moscow_lng], zoom_start=10)


# In[58]:


Choropleth(
    geo_data=state_geo,
    data=middle_avg_bill_district,
    columns=['district', 'middle_avg_bill'],
    key_on='feature.name',
    fill_color='YlGn',
    fill_opacity=0.8,
    legend_name='Медианный чек заведений по округам',
).add_to(m_3)
m_3


# Дороже всего можно поесть - в ЗАО и ЦАО. Дешевле всего - в ЮАО, ЮВАО и СВАО.

# **Общий вывод анализа данных:**
# 
# - Большую долю на рынке занимают кафе(28,3%), около 1/4 (24,3%) - рестораны и почти 17% - кофейни. Меньше 5% рынка занимают столовые, а также булочные.
# 
# - Больше всего посадочных мест в барах, пабах, ресторанах и кофейнях. От всего количества посадочных мест 15.5% составляют рестораны, 14.8% - бары, пабы, 14.5% - кофейни.
# 
# - 38% заведений являются сетевыми. В категории "булочная" 61.3% занимают сети, в категории "пиццерия" - 52.1%, в "кофейнях" - 51%. А в категории "столовая" это значение равняется 28%, в категории "бар, паб" - 22%.
# 
# - Шоколадница, Домино'с пицца, Додо пицца, One price coffee, Яндекс лавка, Cofix - лидеры среди сетевых общепитов. Они входят в категории кофейнь, пиццерий и ресторанов. Му-му, Чайхона, Хинкальная и Буханка состоят из трех и больше типов категорий. Кофейнями практически полностью являются Cofefest, Кофепорт, Cofix, One Price Coffee и Шоколадница. Ресторанами являются Теремок, Prime и Яндекс Лавка. Пиццерии - Додо Пицца и Домино'с Пицца, а кафе - Кулинарная лавка братьев Караваевых.
# 
# - Во всех округах преобладают категории "кафе", "ресторан" и "кофейня". А в ЦАО также много баров, пабов. Меньше всего заведений с такой категорией, как "булочная" и "столовая".
# 
# - Средняя оценка по категориям несильно различается. Однако самый высокий рейтинг в барах, пабах - 4.38, и низкий рейтинг - в кафе(4.12) и быстром питании(4.05).
# 
# - По округам самый высокий средний рейтинг - в ЦАО, чуть ниже - в САО, СЗАО. Ниже всего - в ЮВАО. меньше всего заведений в ЮАО, ЮВАО, ВАО. 
# 
# - По ходу анализа был найдена ошибка в данных: кофейня you&coffee по изначальным данным находилась в САО, хотя по адресу она - в ЮВАО . 
# 
# - Выше всего медианный чек- в ЗАО и ЦАО, ниже всего - в ЮАО, ЮВАО и СВАО
# 
# - Больше всего улиц с одним заведением в ЦАО, что интересно. В СВАО, втором округе по количеству таких улиц, значение меньше - в 2,5 раза. И меньше всего улиц с одним общепитом - в ЮЗАО.

# ### Детализируем исследование: открытие кофейни

# Основателям фонда «Shut Up and Take My Money» не даёт покоя успех сериала «Друзья». Их мечта — открыть такую же крутую и доступную, как «Central Perk», кофейню в Москве. Будем считать, что заказчики не боятся конкуренции в этой сфере, ведь кофеен в больших городах уже достаточно. Попробуйте определить, осуществима ли мечта клиентов.

# Сколько всего кофеен в датасете? В каких районах их больше всего, каковы особенности их расположения?

# In[59]:


print('Всего кофеен в Москве:', df[df['category'] == 'кофейня']['name'].count())


# In[60]:


coffee_house = df[df['category'] == 'кофейня']


# In[61]:


coffee_house_ditrict = coffee_house.groupby('district')['name'].agg({'count'}).sort_values('count', ascending=False).reset_index()
coffee_house_ditrict


# Построим визуализацию.

# In[62]:


m_4 = Map(location=[moscow_lat, moscow_lng], zoom_start=10)


# In[63]:


Choropleth(
    geo_data=state_geo,
    data=coffee_house_ditrict,
    columns=['district', 'count'],
    key_on='feature.name',
    fill_color='YlGn',
    fill_opacity=0.8,
    legend_name='Количество кофеен по районам',
).add_to(m_4)
m_4


# Больше всего кофеен в ЦАО, меньше всего - в ВАО, ЮЗАО, ЮВАО и СЗАО. 

# In[64]:


m_5 = Map(location=[moscow_lat, moscow_lng], zoom_start=10)


# In[65]:


marker_cluster = MarkerCluster().add_to(m_5)


def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

coffee_house.apply(create_clusters, axis=1)

m_5


# Особенности расположения: неудивительно, что больше всего кофейнь в центре города. Чем ближе к МКАДу, тем меньше плотность заведений этой категории.

# Есть ли круглосуточные кофейни?

# In[66]:


coffee_house[coffee_house['is_24/7'] == True]['name'].count()


# Круглосуточных кофеен немного: скорее всего из-за формата заведения.

# In[67]:


coffee_house_24 = coffee_house[coffee_house['is_24/7'] == True]


# In[68]:


coffee_house24_ditrict = coffee_house_24.groupby('district')['name'].count().to_frame().sort_values('name', ascending=False).reset_index()
coffee_house24_ditrict


# In[69]:


sns.set_style('whitegrid')
plt.figure(figsize=(10, 7))
plt.title('Количество круглосуточных кофеен по районам')
sns.barplot(x='name', y='district', data=coffee_house24_ditrict, color='lightblue')
plt.xlabel('Количество')
plt.ylabel(' ')
plt.show()


# Какие у кофеен рейтинги? Как они распределяются по районам?

# In[70]:


ratings = df.groupby('category')['rating'].agg({'mean'}).sort_values('mean', ascending=False).reset_index()
ratings['mean'] = round(ratings['mean'], 3)
ratings


# In[71]:


rating_coffee_house = coffee_house.groupby('district')['rating'].agg({'mean'}).sort_values('mean', ascending=False).reset_index()
rating_coffee_house['mean'] = round(rating_coffee_house['mean'], 3)
rating_coffee_house


# In[72]:


fig_6 = px.bar(rating_coffee_house, x='district', y='mean',
               labels=dict(district=' ', mean='Рейтинг'),
               color_discrete_sequence=['lightblue'], 
              title='Средний рейтинг по округам')
fig_6.update_layout(
    autosize=False,
    width=800,
    height=500,
    yaxis_range=[4, 4.5])
fig_6.show()


# Здесь для визуалицизации достаточно столбчатой диаграммы, поскольку только в ЦАО средний рейтинг немного выше, чем в остальных округах(4.336). В остальных округах рейтинг плюс-минус такой же(4.2-4.3)

# На какую стоимость чашки капучино стоит ориентироваться при открытии и почему?

# Для того, чтобы ответить на данный вопрос, найдем медиану по столбцу 'middle_coffee_cup'.

# In[73]:


coffee_house_middle_coffee_cup = coffee_house.groupby('district')['middle_coffee_cup'].median().to_frame().sort_values('middle_coffee_cup', ascending=False).reset_index()
coffee_house_middle_coffee_cup


# Также построим визуализацию.

# In[74]:


fig_7 = px.bar(coffee_house_middle_coffee_cup, x='district', y='middle_coffee_cup',
               labels=dict(district=' ', middle_coffee_cup='Стоимость чашки капучино'),
               color_discrete_sequence=['lightblue'], 
              title='Медианная стоимость чашки капучино по округам')
fig_7.update_layout(
    autosize=False,
    width=800,
    height=500)
fig_7.show()


# Стоимость одной чашки капучино зависит от раойна в котором кофейня будет находится. Так в ЮЗАО медианная цена одной чашки составляет 198 рублей. В данном районе самая высокая стоимость.

# In[75]:


df_2 = pd.merge(coffee_house_ditrict, rating_coffee_house, how='left', on='district')
df_2 = pd.merge(df_2, coffee_house_middle_coffee_cup, how='left', on='district')
df_2


# In[76]:


sns.heatmap(df_2.corr(), annot = True)


# Построив хитмэп, можно сказать, что стоимость чашки капучино больше зависит от количества заведений в округе(0.4), нежели от рейтинга. Хотя зависимость и слабая, но она присутствует. То есть, чем больше заведений в округе, тем выше стоимость одной чашки. А от рейтинга цена чашки практически не зависит(0.15). Можно также отметить зависимость рейтинга от количества заведений в округе (0.37). Это легко можно объяснить конкурентностью. Чем больше заведений в одном районе, тем выше конкурентность между ними. Соотвественно, эти заведения улучшают качество, чтобы привлечь больше посетителей, откуда у заведений более высокий рейтинг. 
# 
# **Рекомендации**
# 
# Поскольку кофейня только открывается, следует опираться на среднюю цену по округу, в котором будет находится кофейня. Плюс, как сказано в задаче, цель основателей фонда «Shut Up and Take My Money» - доступность новой кофейни. Поэтому цена одной чашки капучино должна примерно варьироваться от 198 до 135 рублей в зависимости от округа.
# Безусловно, для более высокой цены чашки капучино стоит выбирать округ с наибольшей плотностью кофеен. Стоит рассмотреть юг ЦАО и север ЮАО, или ЮЗАО. Там плотность кофеен не слишком высокая, что говорит о не очень большом количество конкурентов, но и не слишком низкая, то есть можно будет установить цену в районе 150 руб. Однако все же надо обращать внимание на стоимость аренды помещения.

# ### Презентация

# https://disk.yandex.ru/i/mR_ad1pAl5aoxw
