import mysql.connector as connector
from config import ConfigParser

with open("../config.json", "r") as _file:
	config = ConfigParser(_file.read())

db = connector.connect(**config.DATABASE)
cursor = db.cursor()

cursor.execute("""CREATE TABLE files (
  `id`INT NOT NULL AUTO_INCREMENT
  `user_id` VARCHAR(20) NULL,
  `file_id` VARCHAR(500) NULL,
  `file_type` VARCHAR(20) NULL,
  `homework` VARCHAR(2)),
   ADD PRIMARY KEY (`id`);""")

cursor.execute("""CREATE TABLE action (
  `message_id` TEXT NULL,
  `chat_id` TEXT NULL DEFAULT NULL,
  `time` TEXT NULL DEFAULT NULL,
  `user_id` TEXT NULL DEFAULT NULL,
  `type` TEXT NULL DEFAULT NULL,
  `first_name` VARCHAR(50) NULL DEFAULT NULL,
  `last_name` VARCHAR(50) NULL DEFAULT NULL,
  `content` TEXT NULL DEFAULT NULL);
""")

cursor.execute("""
	CREATE TABLE `bs_40223`.`users` (
    `user_id` INT NULL,
    `name` VARCHAR(50) NULL,
    `reshte` VARCHAR(10) NULL,
    `paye` INT NULL);
""")

db.commit()
cursor.close()
db.close()