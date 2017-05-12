CREATE_GEO_TABLE = '''
CREATE TABLE geo (
    ip varchar(15) PRIMARY KEY
    , country_code varchar(2) DEFAULT NULL
    , country_name varchar(84) DEFAULT NULL
    , region_code varchar(3) DEFAULT NULL
    , region_name varchar(128) DEFAULT NULL
    , city varchar(128) DEFAULT NULL
    , zip_code varchar(10) DEFAULT NULL
    , time_zone varchar(128) DEFAULT NULL
    , latitude decimal(7,4) DEFAULT NULL
    , longitude decimal(7,4) DEFAULT NULL
    , metro_code int DEFAULT NULL
)
'''
CREATE_RDAP_TABLE = '''
CREATE TABLE rdap (
    ip varchar(15) PRIMARY KEY
    , name varchar(125) DEFAULT NULL
    , country varchar(2) DEFAULT NULL
    , start_address varchar(20) DEFAULT NULL
    , end_address varchar(20) DEFAULT NULL
    , entities text DEFAULT NULL
    , handle varchar(50) DEFAULT NULL
    , ip_version varchar(2) DEFAULT NULL
    , lang varchar(2) DEFAULT NULL
    , parent_handle varchar(50) DEFAULT NULL
    , status varchar(6) DEFAULT NULL
    , type varchar(36) DEFAULT NULL
    , last_changed datetime DEFAULT NULL
    , registration datetime DEFAULT NULL
)
'''

CREATE_TF = '''
CREATE TABLE text_file (
  id SERIAL
  , file_name varchar(128) DEFAULT NULL
  , ip_count int DEFAULT NULL
  , date_uploaded timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
)
'''
MYSQL_CREATE_DB = '''CREATE DATABASE IF NOT EXISTS %s'''

MYSQL_SUPRESS_WARN = '''SET sql_notes = 1'''
DROP_TF = '''DROP TABLE IF EXISTS text_file'''
