from decimal import Decimal
from dotenv import load_dotenv
import os
import mysql.connector
from services.log import log

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")


def get_db_connection(database_name=None):
    return mysql.connector.connect(host=db_host, user=db_user, password=db_pass) if database_name == None else mysql.connector.connect(host=db_host, user=db_user, password=db_pass, database=database_name)

# DB Operations


def init_db():
    log('init_db started...')

    # Connect to db
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    # Create DB if does not exist
    sql = f"CREATE DATABASE IF NOT EXISTS {db_name}"
    cursor.execute(sql)
    log(f"{db_name} table creation is completed")
    db_conn.close()

    # Connect to db within new db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Create tables if do not exist
    sql = '''CREATE TABLE IF NOT EXISTS series (
  id int auto_increment not null,
  serie_id int not null unique,
  name varchar(255) not null,
  overview varchar(1023) not null,
  number_of_seasons smallint unsigned not null,
  number_of_episodes smallint unsigned not null,
  popularity float null,
  vote_average float null,
  vote_count int unsigned null,
  first_air_date date not null,
  last_air_date date null,
  status varchar(255),
  primary key (id)
  )
  '''
    cursor.execute(sql)
    log("series table creation executed")

    sql = '''CREATE TABLE IF NOT EXISTS people (
  id int auto_increment not null,
  person_id int not null unique,
  name varchar(255) not null,
  gender enum('Unspecified', 'Female', 'Male', 'Other') not null,
  known_for_department varchar(255) null,
  popularity float null,
  primary key (id)
  )
  '''
    cursor.execute(sql)
    log("people table creation executed")

    sql = '''CREATE TABLE IF NOT EXISTS assignments (
  id int auto_increment not null,
  person_id int not null,
  serie_id int not null,
  episode_count int not null,
  role enum('Cast', 'Crew') not null,
  `job` varchar(255) null,
  `character` varchar(1023) null,
  primary key (id),
  foreign key (person_id) references people(person_id),
  foreign key (serie_id) references series(serie_id)
  )
  '''
    cursor.execute(sql)
    log("assignments table creation executed")

    db_conn.close()

    log('init_db finished...')
    return


def drop_db():
    log('drop_db started...')

    # Connect to db
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    # Drop DB if  exist
    sql = f"DROP DATABASE IF EXISTS {db_name}"
    cursor.execute(sql)
    log(f"{db_name} database drop is completed")
    db_conn.close()
    return


def insert_series_data(data):
    log("insert_series_data is started")

    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Insert values
    insert_stmt = '''INSERT INTO series (serie_id, name, overview, number_of_seasons, number_of_episodes,
    popularity, vote_average, vote_count, first_air_date, last_air_date, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    insert_data = list(map((lambda x: (
        x['id'],
        x['name'],
        x['overview'],
        x['number_of_seasons'],
        x['number_of_episodes'],
        x['popularity'],
        x['vote_average'],
        x['vote_count'],
        x['first_air_date'],
        x['last_air_date'],
        x['status'])), data))

    cursor.executemany(insert_stmt, insert_data)
    db_conn.commit()
    db_conn.close()

    log("insert_series_data is completed")
    return


def insert_people_data(data):
    log("insert_people_data is started")

    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Insert people values
    insert_stmt = '''INSERT INTO people (person_id, name, gender, known_for_department, popularity)
    VALUES (%s, %s, %s, %s, %s)'''

    distinct_data = list(
        {object_['person_id']: object_ for object_ in data}.values())

    insert_data = list(map((lambda x: (
        x['person_id'],
        x['name'],
        x['gender'] + 1,
        x['known_for_department'],
        x['popularity'])), distinct_data))

    cursor.executemany(insert_stmt, insert_data)
    db_conn.commit()

    # Insert assignment values
    insert_stmt = '''INSERT INTO assignments (person_id, serie_id, episode_count, role, job, `character`)
    VALUES (%s, %s, %s, %s, %s, %s)'''

    insert_data = list(map((lambda x: (
        x['person_id'],
        x['serie_id'],
        x['episode_count'],
        x['role'],
        x.get('job'),
        x.get('character'))), data))

    cursor.executemany(insert_stmt, insert_data)
    db_conn.commit()

    db_conn.close()

    log("insert_people_data is completed")
    return

# Queries


def get_top_ten_acting():
    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Select
    query = """SELECT person_id, name, gender, known_for_department, popularity FROM 
    themoviedb.people where known_for_department='Acting' order by popularity desc limit 10"""
    cursor.execute(query)
    result = cursor.fetchall()

    db_conn.close()

    return result


def get_top_ten_acting_ordered():
    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Select
    query = """SELECT CAST((@cnt := @cnt + 1) as signed) as `Popularity Order`, name as `Actress/Actor's Name`, gender as `Gender`
    FROM themoviedb.people AS temp CROSS JOIN (SELECT @cnt := 0) AS dummy
    where known_for_department='Acting' order by popularity desc limit 10
  """
    cursor.execute(query)
    result = cursor.fetchall()

    db_conn.close()

    return result


def get_directors_work():
    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Select
    query = """SELECT p.name as `Director Name`, s.name as `Series`, a.episode_count as `Episodes Directed`
    from themoviedb.people p 
    join themoviedb.assignments a on p.person_id = a.person_id 
    join themoviedb.series s on a.serie_id = s.serie_id
    where p.known_for_department='Directing' and a.role='Crew' and a.job = 'Director'
    group by a.person_id having count(*) > 1 order by 1 desc;
  """
    cursor.execute(query)
    result = cursor.fetchall()

    db_conn.close()

    return result


def get_top_five_by_categories():
    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Select
    query = """SELECT Acting.row_num as 'Popularity Order', Acting, Directing, Writing from
    (SELECT name as 'Acting', row_number() over (order by popularity desc) as row_num from themoviedb.people where known_for_department = 'Acting' order by popularity desc limit 5) Acting
    JOIN (SELECT name as 'Directing', row_number() over (order by popularity desc) as row_num from themoviedb.people where known_for_department = 'Directing' order by popularity desc limit 5) Directing on Acting.row_num=Directing.row_num
    JOIN (SELECT name as 'Writing', row_number() over (order by popularity desc) as row_num from themoviedb.people where known_for_department = 'Writing' order by popularity desc limit 5) Writing on Directing.row_num=Writing.row_num
  """
    cursor.execute(query)
    result = cursor.fetchall()

    db_conn.close()

    return result


def get_filter_data():
    filter_data = {
        'genders': [],
        'knownfors': []
    }

    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    # Select
    query = "SELECT gender FROM themoviedb.people group by gender order by 1"
    cursor.execute(query)
    filter_data['genders'] = [item[0] for item in cursor.fetchall()]

    query = "SELECT known_for_department FROM themoviedb.people where known_for_department is not null group by known_for_department order by 1;"
    cursor.execute(query)
    filter_data['knownfors'] = [item[0] for item in cursor.fetchall()]

    db_conn.close()

    return filter_data


def get_people(gender, knownfor, page, limit):
    print(gender, knownfor)
    # Connect to db
    db_conn = get_db_connection(db_name)
    cursor = db_conn.cursor()

    empstr = ''
    where_cnd = '' if (gender == None or gender is empstr) and (
        knownfor == None or knownfor is empstr) else 'where '

    if gender is not empstr:
        where_cnd += f'gender="{gender}" '
    if knownfor is not empstr:
        if gender is not empstr:
            where_cnd += 'and '
        where_cnd += f'known_for_department="{knownfor}" '

    # Select
    query = f"SELECT id, name, gender, known_for_department, popularity FROM themoviedb.people {where_cnd} limit {limit} offset {(page - 1) * limit}"

    cursor.execute(query)
    result = cursor.fetchall()

    # Select
    query = f"SELECT count(id) FROM themoviedb.people {where_cnd}"

    cursor.execute(query)
    total = cursor.fetchall()[0]

    db_conn.close()

    data = list(map((lambda x: {
        'key': x[0],
        'name': x[1],
        'gender': x[2],
        'known_for_department': x[3],
        'popularity': x[4]
    }), result))

    return {'data': data, 'total': total[0]}
