import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

from typing import Union, List, Tuple

connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

def film_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego id kategorii.
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''

    if not isinstance(category_id, int):
        return None
    else:
        return pd.read_sql(f'''
        SELECT 
            film.title AS title,
            language.name AS languge, 
            category.name AS category
        FROM category
            INNER JOIN film_category USING(category_id)
            INNER JOIN film USING(film_id)
            INNER JOIN language USING(language_id)
        WHERE 
            category.category_id = {category_id}
        ORDER BY title
        ''', con=connection)

    
def number_films_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów w zadanej kategori przez id kategorii.
    Przykład wynikowej tabeli:
    |   |category   |count|
    |0	|Action 	|64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not isinstance(category_id, int):
        return None
    else:
        return pd.read_sql(f'''SELECT
                            category.name as category,
                            COUNT(*)
                        FROM film
                            JOIN film_category USING(film_id)
                            JOIN category USING(category_id)
                        WHERE 
                            film_category.category_id = {category_id}
                        GROUP BY 
                            category.name''', con = connection)


def number_film_by_length(min_length: Union[int,float] = 0, max_length: Union[int,float] = 1e6 ) :
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów o dla poszczegulnych długości pomiędzy wartościami min_length a max_length.
    Przykład wynikowej tabeli:
    |   |length     |count|
    |0	|46 	    |64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    min_length (int,float): wartość minimalnej długości filmu
    max_length (int,float): wartość maksymalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not isinstance(min_length, (int, float)) or not isinstance(max_length, (int, float)) or max_length < min_length:
        return None
    else:
        return pd.read_sql(f'''SELECT
                            film.length as length,
                            COUNT(*)
                        FROM film
                        WHERE 
                            film.length BETWEEN {min_length} AND {max_length}
                        GROUP BY 
                            film.length''', con = connection)

def client_from_city(city:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o listę klientów z zadanego miasta przez wartość city.
    Przykład wynikowej tabeli:
    |   |city	    |first_name	|last_name
    |0	|Athenai	|Linda	    |Williams
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    city (str): nazwa miaste dla którego mamy sporządzić listę klientów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not isinstance(city, str):
        return None
    else:
        query = f'''SELECT
                        city.city,
                        customer.first_name,
                        customer.last_name 
                    FROM customer
                        JOIN address USING(address_id)
                        JOIN city USING(city_id)
                    WHERE
                        city.city = '{city}' 
                    ORDER BY 
                        customer.first_name, customer.last_name ASC'''

        return pd.read_sql(query, con = connection)

                        
def avg_amount_by_length(length:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o średnią wartość wypożyczenia filmów dla zadanej długości length.
    Przykład wynikowej tabeli:
    |   |length |avg
    |0	|48	    |4.295389
    
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    length (int,float): długość filmu dla którego mamy pożyczyć średnią wartość wypożyczonych filmów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not (isinstance(length, (int, float))):
        return None
    else:
        return pd.read_sql(f'''SELECT
                        film.length,
                        AVG(payment.amount)
                    FROM film
                        JOIN inventory USING(film_id)
                        JOIN rental USING(inventory_id)
                        JOIN payment USING(rental_id)
                    WHERE      
                        film.length = {length}
                    GROUP BY
                        film.length''', con = connection)

def client_by_sum_length(sum_min:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o sumaryczny czas wypożyczonych filmów przez klientów powyżej zadanej wartości.
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |sum
    |0  |Brian	    |Wyman  	|1265
    
    Tabela wynikowa powinna być posortowane według sumy, imienia i nazwiska klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    sum_min (int,float): minimalna wartość sumy długości wypożyczonych filmów którą musi spełniać klient
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not isinstance(sum_min, (int, float)):
        return None
    else:
        return pd.read_sql(f'''SELECT
                            customer.first_name,
                            customer.last_name,
                            SUM(film.length) as sum
                        FROM customer
                            JOIN rental USING(customer_id)
                            JOIN inventory USING(inventory_id)
                            JOIN film USING(film_id)
                        GROUP BY
                            customer.first_name, customer.last_name
                        HAVING  
                            SUM(film.length) > {sum_min}
                        ORDER BY
                            sum, last_name, first_name''', con = connection)  

def category_statistic_length(name:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o statystykę długości filmów w kategorii o zadanej nazwie.
    Przykład wynikowej tabeli:
    |   |category   |avg    |sum    |min    |max
    |0	|Action 	|111.60 |7143   |47 	|185
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    name (str): Nazwa kategorii dla której ma zostać wypisana statystyka
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if not isinstance(name, str):
        return None
    else:
        return pd.read_sql(f'''SELECT
                        category.name as category,
                        AVG(film.length),
                        SUM(film.length),
                        MIN(film.length),
                        MAX(film.length)
                    FROM
                        film
                            JOIN film_category USING(film_id)
                            JOIN category USING(category_id)
                    GROUP BY
                        category.name
                    HAVING 
                        category.name = '{name}' ''', con = connection)  