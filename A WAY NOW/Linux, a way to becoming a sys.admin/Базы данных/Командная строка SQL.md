*SHOW DATABASES; или `\l`*- выводит все бд
*CREATE DATABASE (name);* - создаст новую бд
*DROP DATABASE (name;* - для удаления бд
*USE (db);* - для использования конкретной бд
*show tables;* - показывает все таблицы в бд
*show columns FROM (nt);* - покажет все столбцы в определённой таблице и их настройки
`\q` - выход из командой строки или же ctrl+d
`\du` - список пользователей 
*ALTER USER username WITH PASSWORD 'password';* - добавление пароля для пользователей
*CREATE USER username WITH PASSWORD 'password';* - создание пользователя
*ALTER USER username WITH SUPERUSER;* - даёт пользователю права суперпользователя
*DROP USER username;* - чтобы удалить пользователя

# Создание таблиц

***Пример создания связанных таблиц***

CREATE TABLE `teacher`(
id int auto_increment primary key,
surname VARCHAR(255) NOT NULL
);

*id* - обозначает уникальный идентификатор
*INT* - указывает `id`, что тот будет целочисленым
*AUTO_INCREMENT* - автоинкрементация, указывает что каждая последующая запись будет иметь значение на единицу больше предыдущего
*PRIMARY KEY* - указывает что `id` первичный ключ
*VARCHAR* - строковое значение с ограничением на 255 символов
*NOT NULL* - означает что `surname` не может быть пустым

CREATE TABLE `lesson`(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL,
teacher_id INT NOT NULL, 
FOREIGN KEY (`teacher_id`) references `teacher`(id)
);

*FOREIGN KEY and REFERENCES* - указывает что `teacher_id` в этой таблице, будет является внешним ключём, который будет связан с колонкой `id` из таблица `teacher`. *lesson(teacher_id) = teacher(id)*

# Изменение данных таблиц

*INSERT INTO* teacher (surname) values ("Иванов"); - добавляет в таблицу *teacher* в колонку *surname* 'Иванов'
Кавычки добавляются, так как surname является текстовой формой.
*ALTER TABLE teacher ADD age INT;* - добавление колонок в существующую таблицу
*UPDATE teacher SET age = 20 WHERE id=1;* - обновить существующую таблицу данными, а именно поле *age*, где *id=1*
*DELETE FROM teacher WHERE id = 6;* - удалить строку в таблице где колонка id = 6

# Просмотр данных из таблиц

*SELECT * FROM teacher;* - выведит всю таблицу `teacher`, чтобы вытащить определённую колонку нужно поменять * на необходимое, можно указать через запятую
*SELECT DISTINCT surname FROM teacher;* - выводит только уникальные значения из колонки surname
*SELECT * FROM teacher WHERE id = 1 ***LIMIT 2***; - условие, при котором выводятся данные где id=1, можно использовать знаки больше и меньше, если поле *строчное*, значение помещаетс в кавычки. ***LIMIT 2***, задаёт ограничение на вывод только *2* строк.
*SELECT * FROM teacher WHERE surname LIKE "п%ов";* - условие при котором *LIKE* задаётся значение, которое будет выведено, `%` означает любое количество символов в промежутке между `п` и `ов` 
*SELECT id AS 'Идентификатор', surname AS 'Фамилия' FROM teacher;* - заменит id и surname на выводе, на удобные для чтения слова
*SELECT * FROM teacher ORDER BY surname ***DESC***; - сортировка значений, в случае строчного, выводить в порядке алфавита, в случае числового, по возрастанию. ***DESC*** сортирует вывод в обратном порядке.
*SELECT * FROM teacher WHERE id > 3 AND age < 45;* - выполнится запрос где будет выполнено. Вместо *AND*, также можно использовать *OR*
*SELECT * FROM teacher WHERE NOT id = 2;* - условие, при котором выполняется вывод *id* **НЕ** равный двум.
*SELECT * FROM teacher WHERE age BETWEEN 35 and 45;* - условие при котором *age* равняется 35, 45 и всем цифрам находящимся в этом промежутке, если таковы имеются в таблице.

# Объединение таблиц

Существует два типы соединений **INNER (внутренний) JOIN** и **OUTER (внешний) JOIN** 

***JOIN***
При выполнении стандартного INNER JOIN или просто JOIN, то в исходную таблицу попадут только те записи, где для каждого учителя есть урок, те учителя которые не ведут урок, в исходную таблицу не попадают.
![[Pasted image 20230519180143.png]]
*SELECT teacher.surname, lesson.name FROM teacher JOIN lesson ON teacher.id = lesson.id;* - из таблица *teacher* берётся колонка surname, из *lesson* колонку name, затем указывается левая таблица с которой будет происходить объединение, после *JOIN* пишется правая таблица с которой будет происходить объединение, после чего пишется *ON* и столбцы по которым будет происходить объединение *teacher.id* и *lesson.id* по скольку они являются связующими, *primary key* и *foreign key* непосредственно

***OUTER JOIN***
Бывает *Left Outer Join* и *Right Outer Join*
![[Pasted image 20230519180125.png]]
В случае *левостороннего*, в исходную таблицу попадают все учителя, не важно, ведут ли они какие-то уроки или нет.
*SELECT teacher.surname, lesson.name FROM teacher LEFT JOIN lesson ON teacher.id = lesson.id;*
В случае *правостороннего* наоборот, попадают только уроки
*SELECT teacher.surname, lesson.name FROM teacher RIGHT JOIN lesson ON teacher.id = lesson.id;*

***FULL JOIN***
Полное соединение, здесь в выборку попадают абсолютно все значения таблиц
![[Pasted image 20230519180303.png]]
*SELECT teacher.surname, lesson.name FROM teacher FULL OUTER JOIN lesson ON teacher.id = lesson.id;*

***Вертикальное объединение***
*SELECT * FROM teacher UNION SELECT * FROM lesson;*

# Функции 

*SELECT AVG(age) FROM teacher;* - функция AVG возращает средний возраст столбца *age*
*SELECT MAX(age), MIN(age) FROM teacher;* - выведет максимальное и минимальное значение столбца *age*
*SELECT SUM(age) FROM teacher;* - сумма всех значений, которые попадают в выборку
*SELECT age, COUNT(age) FROM teacher GROUP BY age;* - посчитает по столбцу *age* и с группирует их по порядку при помощи *GROUP BY* 
![[Pasted image 20230519192131.png]]

# Индексы


[[СУБД]] [[postgreSQL (БД)]] [[SQL vs NoSQL (реляционная и нерялицонная)]]
#СУБД #postgresql #psql #sql 