-- Active: 1758538193616@@finaissistdb.cluyie2u4ldc.ap-northeast-2.rds.amazonaws.com@3306@mysql
DROP DATABASE finaissistdb;

CREATE DATABASE finaissistdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ebroot'@'finaissistdb.cluyie2u4ldc.ap-northeast-2.rds.amazonaws.com' IDENTIFIED BY 'finaissistdb.cluyie2u4ldc.ap-northeast-2.rds.amazonaws.com';
GRANT ALL PRIVILEGES ON finaissistdb.* TO 'ebroot'@'finaissistdb.cluyie2u4ldc.ap-northeast-2.rds.amazonaws.com';
FLUSH PRIVILEGES;


use finaissistdb;
show tables;

-- f_chatbot 기록 삭제
DELETE FROM django_migrations WHERE app='f_chatbot';

-- f_calendar, f_todo 같은 다른 앱들도 f_user 보다 먼저 들어간 게 있으면 삭제
DELETE FROM django_migrations WHERE app='f_calendar';
DELETE FROM django_migrations WHERE app='f_todo';
DELETE FROM django_migrations WHERE app='f_document';