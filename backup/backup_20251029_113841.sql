/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.11-MariaDB, for Linux (x86_64)
--
-- Host: 134.90.167.42    Database: project_Schlegel
-- ------------------------------------------------------
-- Server version	10.6.22-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Cars`
--

DROP TABLE IF EXISTS `Cars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cars` (
  `CarID` int(5) NOT NULL COMMENT 'ID машины',
  `brand` varchar(30) NOT NULL COMMENT 'Марка автомобиля',
  `year` int(4) NOT NULL COMMENT 'Год выпуска',
  `model` varchar(20) NOT NULL COMMENT 'Модель',
  `licensePlate` varchar(9) NOT NULL COMMENT 'ГОС номер',
  `vin` varchar(17) DEFAULT NULL COMMENT 'VIN номер',
  `engineNumber` varchar(20) DEFAULT NULL COMMENT 'Номер двигателя',
  `color` varchar(20) DEFAULT NULL COMMENT 'Цвет',
  `power` int(4) DEFAULT NULL COMMENT 'Мощность (л.с.)',
  `lastMaintenance` date DEFAULT NULL COMMENT 'Дата последнего ТО',
  `nextMaintenance` date DEFAULT NULL COMMENT 'Дата следующего ТО',
  `maintenanceInterval` int(4) DEFAULT 10000 COMMENT 'Интервал ТО (км)',
  `notes` text DEFAULT NULL COMMENT 'Заметки',
  `mileage` int(7) NOT NULL COMMENT 'Пробег',
  `status` enum('Active','Inactive','Maintenance','Retired') NOT NULL DEFAULT 'Active',
  PRIMARY KEY (`CarID`),
  UNIQUE KEY `CarID` (`CarID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Машины';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cars`
--

LOCK TABLES `Cars` WRITE;
/*!40000 ALTER TABLE `Cars` DISABLE KEYS */;
INSERT INTO `Cars` VALUES
(1,'Renault',2023,'Premium 400','H629CE142','VF1CE6BLQPZ7LGKUP','OWO5839PH741','White',400,'2025-07-21','2025-08-30',8000,'Замена водяной помпы',61056,'Maintenance'),
(2,'Renault',2023,'Premium 400','X740XC42','VF1J1AQML1FKCM10J','04932DJ11614','White',400,'2025-10-05','2025-11-14',8000,'Новый аккумулятор',76449,'Active'),
(3,'Scania',2020,'G410','M043CK142','YS2WQHV81ZOINSFI8','VTA2864FV096','Blue',410,'2025-09-19','2025-11-18',12000,'Проверка рулевого управления',125960,'Active'),
(4,'Scania',2020,'R500','P959KP42','YS2Q31J35HHFBZV0D','68388ZV70819','Silver',500,'2025-08-16','2025-10-15',12000,'Регулярное ТО выполнено',210898,'Active'),
(5,'DAF',2017,'XF 460','X887EO142','XLR9UJ4NWJA0BZSRC','92448YQ60670','Silver',460,'2025-10-03','2025-12-17',15000,'Нет замечаний',330516,'Inactive'),
(6,'MAN',2022,'TGS 33.440','X456CT142','WMAF9A5MSR4DP6XGT','WBD5688TF053','Blue',440,'2025-08-07','2025-09-26',10000,'Частые поломки',88726,'Maintenance'),
(7,'Renault',2019,'Premium 420','H774KP42','VF1SMFQ41GEDSFLXT','NNA6987QT348','White',420,'2025-10-06','2025-12-05',12000,'Топливный фильтр заменен',173184,'Active'),
(8,'Renault',2019,'Premium 400','C759PT142','VF1D40ICYXXC5V6RW','BBN7214GT295','Blue',400,'2025-11-26','2026-01-25',12000,'Проверка тормозов',192937,'Active'),
(9,'Renault',2019,'Premium 400','E234TB42','VF1N9G82EYL91WXK2','38806KQ67466','Red',400,'2025-10-15','2025-12-14',12000,'Нет замечаний',229635,'Active'),
(10,'Renault',2019,'Premium 420','T753EK42','VF1IVZ6M9XS0PU15N','07311VY61748','Red',420,'2025-11-01','2025-12-31',12000,'Новый аккумулятор',157694,'Active'),
(11,'Iveco',2018,'Stralis 440','H701OK42','ZCFVN5M4OCJ735RAV','17675YB42394','Blue',440,'2025-08-12','2025-10-26',15000,'Новый аккумулятор',198413,'Active'),
(12,'Iveco',2018,'Stralis 480','X819BT142','ZCFQKPXSD3228UA0G','NBZ4972PY937','Red',480,'2025-09-26','2025-12-10',15000,'Замена масла',286602,'Active'),
(13,'Iveco',2018,'Stralis 440','T046CA42','ZCF68PEYVQ2SN1YSE','64447KR25325','White',440,'2025-11-17','2026-01-31',15000,'Техосмотр пройден',311262,'Active'),
(14,'Iveco',2018,'Stralis 440','C156BA142','ZCF3ARPC0Q07QZ6E8','BGB0158ED291','Blue',440,'2025-10-30','2026-01-13',15000,'Новый аккумулятор',279383,'Active'),
(15,'Iveco',2021,'Stralis 480','C767TH42','ZCF9970RY5E2Z5WET','EDY1403EJ977','Red',480,'2025-07-28','2025-09-16',10000,'Проблема с охлаждением',148856,'Maintenance'),
(16,'Iveco',2021,'Stralis 440','H978AC42','ZCF150BTU6Q9BSPD1','41423MJ12501','Red',440,'2025-11-18','2026-01-07',10000,'Новый аккумулятор',116502,'Active'),
(17,'Iveco',2021,'Stralis 440','H385KA142','ZCFZ9THW6XYTNWQ41','XKY9865WX439','White',440,'2025-10-05','2025-11-24',10000,'Замена воздушного фильтра',161482,'Active'),
(18,'Volvo',2020,'FH16 500','M653CC42','YV37CZX1YJ5ZLTRMR','14658JH26451','Blue',500,'2025-08-10','2025-10-09',12000,'Проверка рулевого управления',163074,'Active'),
(19,'Volvo',2020,'FM 420','X479KP42','YV3ASE2P9KSL4KI61','OJE7948QT368','Silver',420,'2026-01-11','2026-03-12',12000,'Диагностика ABS',165261,'Active'),
(20,'Volvo',2020,'FH16 500','K083CY42','YV3E34M4Y4JEQ8M7R','01003ZJ14149','Red',500,'2025-07-23','2025-09-21',12000,'Требуется ремонт КПП',124291,'Maintenance'),
(21,'Renault',2022,'Premium 400','C674KO142','VF1WBCK4VGVALYPLH','DNO1931AH946','White',400,'2025-11-11','2025-12-31',10000,'Топливный фильтр заменен',104393,'Active'),
(22,'Renault',2022,'Premium 400','Y966HE42','VF1MRY2HJMN06Q9V9','19268WV44987','Red',400,'2025-09-27','2025-11-16',10000,'Регулярное ТО выполнено',98366,'Active'),
(23,'Renault',2022,'Premium 420','A296CB42','VF1LTFNIY52X50QX8','IES0521NG225','Silver',420,'2025-08-11','2025-09-30',10000,'Проверка подвески',124532,'Active'),
(24,'КАМАЗ',2018,'6520','T940OO142','XTA0LAVY3F6HRT460','85483VQ23071','Yellow',300,'2025-11-09','2026-01-23',15000,'Не подлежит ремонту',208326,'Retired'),
(25,'MAN',2017,'TGX 18.500','O503KA142','WMA3OTB9SZNVPWOC9','TFI3957VM575','White',500,'2025-08-16','2025-10-30',15000,'Замена воздушного фильтра',260261,'Active'),
(26,'DAF',2021,'XF 460','Y385OO42','XLRC8PIPHMR0MNHKE','PSB1149HD570','Silver',460,'2025-09-20','2025-11-09',10000,'Замена масла',105210,'Active');
/*!40000 ALTER TABLE `Cars` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER trg_prevent_updates_on_retired
BEFORE UPDATE ON Cars
FOR EACH ROW
BEGIN
    -- Если статус "Retired", то вообще нельзя ничего менять
    IF OLD.status = 'Retired' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Нельзя изменять данные автомобиля со статусом "Retired".';
    END IF;
    
    -- Если статус не "Retired", то проверяем запрещённые поля
    -- Поля, которые нельзя менять никогда
    IF NEW.brand != OLD.brand OR
       NEW.year != OLD.year OR
       NEW.model != OLD.model OR
       NEW.vin != OLD.vin OR
       NEW.engineNumber != OLD.engineNumber THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Поля brand, year, model, vin, engineNumber нельзя изменять.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `Maintenance`
--

DROP TABLE IF EXISTS `Maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Maintenance` (
  `maintenanceID` int(5) NOT NULL COMMENT 'ID Обслуживания',
  `carID` int(5) NOT NULL COMMENT 'ID Машины',
  `typeID` int(5) NOT NULL COMMENT 'Тип обслуживания',
  `priority` enum('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT 'Приоритет',
  `userID` int(5) NOT NULL COMMENT 'Назначенный механик',
  `startDate` date NOT NULL COMMENT 'Дата начала',
  `completeDate` date DEFAULT NULL COMMENT 'Дата завершения',
  `description` text NOT NULL COMMENT 'Описание',
  `partsCost` decimal(10,2) DEFAULT NULL COMMENT 'Стоимость запчастей',
  `laborCost` decimal(10,2) DEFAULT 0.00 COMMENT 'Стоимость работ',
  `totalCost` decimal(10,2) GENERATED ALWAYS AS (`partsCost` + `laborCost`) STORED COMMENT 'Общая стоимость',
  `mileageAtService` int(7) DEFAULT NULL COMMENT 'Пробег при обслуживании',
  `nextServiceDate` date DEFAULT NULL COMMENT 'Дата следующего обслуживания',
  `nextServiceMileage` int(7) DEFAULT NULL COMMENT 'Пробег следующего обслуживания',
  `status` enum('planned','in_progress','completed','cancelled','on_hold') NOT NULL DEFAULT 'planned' COMMENT 'Статус',
  PRIMARY KEY (`maintenanceID`),
  UNIQUE KEY `maintenanceID` (`maintenanceID`,`carID`,`userID`),
  KEY `carID` (`carID`),
  KEY `userID` (`userID`),
  KEY `typeID` (`typeID`) USING BTREE,
  CONSTRAINT `Maintenance_ibfk_1` FOREIGN KEY (`carID`) REFERENCES `Cars` (`CarID`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `Maintenance_ibfk_2` FOREIGN KEY (`typeID`) REFERENCES `MaintenanceTypes` (`typeID`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `Maintenance_ibfk_4` FOREIGN KEY (`userID`) REFERENCES `Users` (`userID`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Обслуживание';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Maintenance`
--

LOCK TABLES `Maintenance` WRITE;
/*!40000 ALTER TABLE `Maintenance` DISABLE KEYS */;
INSERT INTO `Maintenance` VALUES
(1,1,1,'medium',2,'2025-07-20','2025-07-21','Плановое ТО. Замена масла, фильтров, проверка систем.',12000.00,3000.00,15000.00,60256,'2025-08-30',68256,'completed'),
(2,2,2,'medium',3,'2025-10-04','2025-10-05','Замена моторного масла и масляного фильтра.',2500.00,500.00,3000.00,76049,'2025-11-14',80049,'completed'),
(3,3,3,'low',4,'2025-09-18','2025-09-19','Компьютерная диагностика двигателя и АКПП. Замечаний нет.',0.00,4000.00,4000.00,125860,'2025-11-18',137860,'completed'),
(4,4,1,'medium',5,'2025-08-15','2025-08-16','Регулярное ТО. Замена всех технических жидкостей.',14500.00,3500.00,18000.00,210798,'2025-10-15',222798,'completed'),
(5,5,1,'medium',2,'2025-10-02','2025-10-03','Плановое ТО. Машина готовится к консервации.',11000.00,4000.00,15000.00,330416,NULL,NULL,'completed'),
(6,7,8,'medium',3,'2025-10-05','2025-10-06','Замена старого аккумулятора на новый. Пусковой ток 800 А.',4500.00,500.00,5000.00,173084,'2025-12-05',185084,'completed'),
(7,10,8,'medium',4,'2025-10-31','2025-11-01','Установлен новый аккумулятор. Профилактическая замена.',4700.00,300.00,5000.00,157594,'2025-12-31',167594,'completed'),
(8,11,8,'medium',5,'2025-08-11','2025-08-12','Замена аккумулятора. Старый не держал заряд.',4800.00,200.00,5000.00,198313,'2025-10-26',213313,'completed'),
(9,12,2,'low',2,'2025-09-25','2025-09-26','Замена масла после длительного рейса.',2800.00,500.00,3300.00,286502,'2025-12-10',301502,'completed'),
(10,13,1,'medium',3,'2025-11-16','2025-11-17','Полное ТО. Пройден техосмотр. Автомобиль в отличном состоянии.',13500.00,4500.00,18000.00,311162,'2026-01-31',323162,'completed'),
(11,14,8,'medium',4,'2025-10-29','2025-10-30','Замена аккумулятора. Плановая по сроку службы.',4600.00,400.00,5000.00,279283,'2026-01-13',294283,'completed'),
(12,16,8,'medium',5,'2025-11-17','2025-11-18','Установка нового АКБ. Старый вышел из строя.',4900.00,100.00,5000.00,116402,'2026-01-07',126402,'completed'),
(13,17,7,'medium',2,'2025-10-04','2025-10-05','Диагностика и проверка подвески. Замена сайлентблоков.',3000.00,2000.00,5000.00,161382,'2025-11-24',176382,'completed'),
(14,18,7,'low',3,'2025-08-09','2025-08-10','Проверка рулевого управления и элементов подвески. Люфтов нет.',0.00,2500.00,2500.00,162974,'2025-10-09',174974,'completed'),
(15,21,2,'medium',4,'2025-11-10','2025-11-11','Замена масла и топливного фильтра.',3500.00,500.00,4000.00,104293,'2025-12-31',114293,'completed'),
(16,22,1,'medium',5,'2025-09-26','2025-09-27','Плановое ТО. Замена масла, фильтров, диагностика.',12500.00,2500.00,15000.00,98266,'2025-11-16',108266,'completed'),
(17,23,7,'low',2,'2025-08-10','2025-08-11','Плановый осмотр подвески. Замена одной сайлентблоки.',1500.00,1500.00,3000.00,124432,'2025-09-30',139432,'completed'),
(18,25,7,'medium',3,'2025-08-15','2025-08-16','Диагностика подвески. Замена амортизаторов.',4000.00,1000.00,5000.00,260161,'2025-10-30',275161,'completed'),
(19,26,2,'medium',4,'2025-09-19','2025-09-20','Замена моторного масла. Использовано синтетическое масло 5W-40.',3200.00,800.00,4000.00,105110,'2025-11-09',115110,'completed'),
(20,19,3,'high',5,'2026-01-10','2026-01-11','Диагностика системы ABS. Замена датчика.',5500.00,2500.00,8000.00,165161,'2026-03-12',177161,'completed'),
(21,1,4,'high',2,'2025-09-14',NULL,'Замена передних тормозных колодок и дисков. Износ критический.',6500.00,3000.00,9500.00,61556,NULL,NULL,'in_progress'),
(22,6,3,'critical',3,'2025-09-13',NULL,'Диагностика частых поломок. Поиск основной причины неисправностей.',0.00,0.00,0.00,89000,NULL,NULL,'in_progress'),
(23,15,3,'high',4,'2025-09-14',NULL,'Диагностика системы охлаждения. Подозрение на течь в радиаторе.',0.00,0.00,0.00,149000,NULL,NULL,'in_progress'),
(24,20,3,'high',5,'2025-09-12',NULL,'Диагностика КПП для оценки стоимости ремонта.',0.00,0.00,0.00,124500,NULL,NULL,'in_progress'),
(25,2,1,'medium',2,'2025-11-14',NULL,'Запланированное плановое ТО. Замена масла, фильтров, диагностика.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(26,3,1,'medium',3,'2025-11-18',NULL,'Плановое ТО по пробегу. Замена масла, фильтров, ремней.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(27,4,4,'medium',4,'2025-10-15',NULL,'Замена задних тормозных колодок. Плановая по пробегу.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(28,7,1,'medium',5,'2025-12-05',NULL,'Плановое ТО. Замена масла, фильтров, свечей.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(29,8,4,'medium',2,'2025-11-26',NULL,'Проверка и замена тормозных колодок (плановые работы).',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(30,9,1,'medium',3,'2025-12-14',NULL,'Плановое техническое обслуживание.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(31,10,1,'medium',4,'2025-12-31',NULL,'Плановое ТО. Замена масла, фильтров, диагностика систем.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(32,11,1,'medium',5,'2025-10-26',NULL,'Плановое ТО по интервалу пробега.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(33,12,1,'medium',2,'2025-12-10',NULL,'Плановое ТО. Замена масла, фильтров, тормозной жидкости.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(34,13,2,'medium',3,'2026-01-31',NULL,'Промежуточная замена масла.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(35,14,1,'medium',4,'2026-01-13',NULL,'Плановое ТО. Полное обслуживание автомобиля.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(36,16,1,'medium',5,'2026-01-07',NULL,'Плановое ТО. Замена масла, фильтров, диагностика.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(37,17,1,'medium',2,'2025-11-24',NULL,'Плановое ТО после замены фильтра.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(38,18,1,'medium',3,'2025-10-09',NULL,'Плановое ТО. Замена масла, фильтров.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(39,19,1,'medium',4,'2026-03-12',NULL,'Плановое ТО после ремонта ABS.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(40,21,1,'medium',5,'2025-12-31',NULL,'Плановое ТО. Комплексное обслуживание.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(41,22,2,'medium',2,'2025-11-16',NULL,'Промежуточная замена масла.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(42,23,1,'medium',3,'2025-09-30',NULL,'Плановое ТО. Замена масла, фильтров.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(43,25,1,'medium',4,'2025-10-30',NULL,'Плановое ТО. Замена масла, фильтров, тормозной жидкости.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(44,26,1,'medium',5,'2025-11-09',NULL,'Плановое ТО. Комплексное обслуживание.',NULL,NULL,NULL,NULL,NULL,NULL,'planned'),
(45,6,5,'high',2,'2025-09-20',NULL,'Ожидание поставки ремня ГРМ и роликов.',15000.00,7000.00,22000.00,89200,NULL,NULL,'on_hold'),
(46,15,6,'medium',3,'2025-09-16',NULL,'Ожидание поставки комплекта свечей зажигания.',2500.00,1000.00,3500.00,149200,NULL,NULL,'on_hold'),
(47,20,5,'critical',4,'2025-09-15',NULL,'Ожидание решения руководства по капитальному ремонту КПП.',NULL,NULL,NULL,124600,NULL,NULL,'on_hold'),
(48,24,1,'low',5,'2025-11-10',NULL,'ТО отменено. Автомобиль снят с эксплуатации.',NULL,NULL,NULL,NULL,NULL,NULL,'cancelled'),
(49,5,2,'low',2,'2025-12-01',NULL,'Замена масла отменена. Автомобиль переведен в неактивный статус.',NULL,NULL,NULL,NULL,NULL,NULL,'cancelled'),
(50,8,3,'low',3,'2025-10-10',NULL,'Диагностика отменена. Проблема не подтвердилась.',NULL,NULL,NULL,NULL,NULL,NULL,'cancelled');
/*!40000 ALTER TABLE `Maintenance` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER before_maintenance_insert_check
BEFORE INSERT ON Maintenance
FOR EACH ROW
BEGIN
    DECLARE car_mileage INT;
    DECLARE last_service_date DATE;
    
    SELECT mileage, lastMaintenance INTO car_mileage, last_service_date 
    FROM Cars WHERE CarID = NEW.carID;
    
    -- Если пробег при обслуживании меньше текущего пробега автомобиля
    IF NEW.mileageAtService < car_mileage THEN
        SET NEW.mileageAtService = car_mileage;
    END IF;
    
    -- Если дата начала раньше последнего ТО
    IF last_service_date IS NOT NULL AND NEW.startDate < last_service_date THEN
        SET NEW.startDate = last_service_date;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER after_maintenance_insert 
AFTER INSERT ON Maintenance
FOR EACH ROW
BEGIN
    IF NEW.status = 'in_progress' THEN
        UPDATE Cars SET status = 'Maintenance' WHERE CarID = NEW.carID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER after_maintenance_status_update 
AFTER UPDATE ON Maintenance
FOR EACH ROW
BEGIN
    IF NEW.status = 'in_progress' AND OLD.status != 'in_progress' THEN
        UPDATE Cars SET status = 'Maintenance' WHERE CarID = NEW.carID;
    END IF;
    
    IF (NEW.status = 'completed' OR NEW.status = 'cancelled') AND OLD.status = 'in_progress' THEN
        UPDATE Cars SET status = 'Active' WHERE CarID = NEW.carID;
    END IF;
    
    IF NEW.status = 'on_hold' AND OLD.status != 'on_hold' THEN
        UPDATE Cars SET status = 'Maintenance' WHERE CarID = NEW.carID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER after_maintenance_complete 
AFTER UPDATE ON Maintenance
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE Cars 
        SET mileage = NEW.mileageAtService,
            lastMaintenance = NEW.completeDate,
            nextMaintenance = NEW.nextServiceDate
        WHERE CarID = NEW.carID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `MaintenanceTypes`
--

DROP TABLE IF EXISTS `MaintenanceTypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `MaintenanceTypes` (
  `typeID` int(5) NOT NULL COMMENT 'ID типа обслуживания',
  `name` varchar(50) NOT NULL COMMENT 'Название',
  `description` text DEFAULT NULL COMMENT 'Описание',
  `intervalKm` int(7) DEFAULT NULL COMMENT 'Интервал по пробегу (км)',
  `intervalDays` int(4) DEFAULT NULL COMMENT 'Интервал по дням',
  `estimatedDuration` int(3) DEFAULT NULL COMMENT 'Ожидаемая продолжительность (часы)',
  `estimatedCost` decimal(10,2) DEFAULT NULL COMMENT 'Ожидаемая стоимость',
  PRIMARY KEY (`typeID`),
  UNIQUE KEY `typeID` (`typeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Типы обслуживания';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MaintenanceTypes`
--

LOCK TABLES `MaintenanceTypes` WRITE;
/*!40000 ALTER TABLE `MaintenanceTypes` DISABLE KEYS */;
INSERT INTO `MaintenanceTypes` VALUES
(1,'Плановое ТО','Регулярное техническое обслуживание',10000,365,4,15000.00),
(2,'Замена масла','Замена моторного масла и фильтров',5000,180,1,3000.00),
(3,'Диагностика','Компьютерная диагностика систем',0,30,2,5000.00),
(4,'Замена тормозных колодок','Замена тормозных колодок и дисков',20000,0,3,8000.00),
(5,'Замена ремня ГРМ','Замена ремня газораспределительного механизма',60000,0,6,12000.00),
(6,'Замена свечей зажигания','Замена свечей зажигания',30000,0,1,2000.00),
(7,'Проверка подвески','Диагностика и ремонт подвески',15000,0,4,10000.00),
(8,'Замена аккумулятора','Замена автомобильного аккумулятора',0,1095,1,5000.00);
/*!40000 ALTER TABLE `MaintenanceTypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Reminders`
--

DROP TABLE IF EXISTS `Reminders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Reminders` (
  `reminderID` int(5) NOT NULL COMMENT 'ID напоминания',
  `reminderType` enum('maintenance','inspection','insurance','license','other') NOT NULL DEFAULT 'maintenance' COMMENT 'Тип напоминания',
  `priority` enum('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT 'Приоритет',
  `isRecurring` enum('true','false') NOT NULL DEFAULT 'false' COMMENT 'Повторяющееся',
  `recurrenceInterval` int(4) DEFAULT NULL COMMENT 'Интервал повторения (дни)',
  `createdAt` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Дата создания',
  `maintenanceID` int(5) NOT NULL COMMENT 'ID обслуживания',
  `remindDate` date NOT NULL COMMENT 'Дата напоминания',
  `message` text NOT NULL COMMENT 'Сообщение',
  `isSent` enum('true','false') NOT NULL COMMENT 'Отправлено ли',
  PRIMARY KEY (`reminderID`),
  UNIQUE KEY `reminderID` (`reminderID`),
  UNIQUE KEY `maintenanceID` (`maintenanceID`),
  CONSTRAINT `fk_reminders_maintenance` FOREIGN KEY (`maintenanceID`) REFERENCES `Maintenance` (`maintenanceID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Напоминания';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Reminders`
--

LOCK TABLES `Reminders` WRITE;
/*!40000 ALTER TABLE `Reminders` DISABLE KEYS */;
INSERT INTO `Reminders` VALUES
(1,'maintenance','low','false',NULL,'2025-09-11 23:36:21',1,'2023-05-11','Напоминание: Замена масла и фильтров запланирована на 10 июня 2023','true'),
(2,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',2,'2023-06-15','Напоминание: Техническое обслуживание запланировано на 15 июля 2023','false'),
(3,'maintenance','high','false',NULL,'2025-09-11 23:36:21',3,'2023-07-04','Напоминание: Ремонт тормозной системы запланирован на 3 августа 2023','false'),
(4,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',4,'2023-08-12','Напоминание: Замена шин запланирована на 12 сентября 2023','true'),
(5,'inspection','low','false',NULL,'2025-09-11 23:36:21',5,'2023-09-19','Напоминание: Диагностика двигателя запланирована на 20 октября 2023','true'),
(6,'maintenance','critical','false',NULL,'2025-09-11 23:36:21',6,'2023-10-05','Напоминание: Замена ремня ГРМ запланирована на 5 ноября 2023','false'),
(7,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',7,'2023-11-10','Напоминание: Ремонт коробки передач запланирован на 10 декабря 2023','true'),
(8,'maintenance','low','false',NULL,'2025-09-11 23:36:21',8,'2023-12-15','Напоминание: Плановое ТО запланировано на 15 января 2024','false'),
(9,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',9,'2024-01-01','Напоминание: Замена радиатора запланирована на 1 февраля 2024','true'),
(10,'maintenance','high','false',NULL,'2025-09-11 23:36:21',10,'2024-01-10','Напоминание: Ремонт подвески запланирован на 10 февраля 2024','false'),
(11,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',11,'2024-02-05','Напоминание: Замена топливного фильтра запланирована на 5 марта 2024','true'),
(12,'maintenance','critical','false',NULL,'2025-09-11 23:36:21',12,'2024-02-18','Напоминание: Капитальный ремонт двигателя запланирован на 18 марта 2024','true'),
(13,'inspection','medium','false',NULL,'2025-09-11 23:36:21',13,'2024-03-01','Напоминание: Проверка электрики запланирована на 1 апреля 2024','true'),
(14,'maintenance','low','false',NULL,'2025-09-11 23:36:21',14,'2024-03-10','Напоминание: Замена воздушного фильтра запланирована на 10 апреля 2024','true'),
(15,'maintenance','medium','false',NULL,'2025-09-11 23:36:21',15,'2024-04-05','Напоминание: Ремонт выхлопной системы запланирован на 5 мая 2024','false');
/*!40000 ALTER TABLE `Reminders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Repairs`
--

DROP TABLE IF EXISTS `Repairs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Repairs` (
  `repairID` int(5) NOT NULL AUTO_INCREMENT COMMENT 'ID ремонта',
  `repairType` enum('engine','transmission','brakes','electrical','body','other') NOT NULL DEFAULT 'other' COMMENT 'Тип ремонта',
  `priority` enum('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT 'Приоритет',
  `status` enum('planned','in_progress','completed','cancelled') NOT NULL DEFAULT 'planned' COMMENT 'Статус',
  `warrantyExpiry` date DEFAULT NULL COMMENT 'Срок гарантии',
  `carID` int(5) NOT NULL COMMENT 'ID Машины',
  `date` date NOT NULL COMMENT 'Дата',
  `reason` text NOT NULL COMMENT 'Причина',
  `description` text NOT NULL COMMENT 'Описание',
  `cost` decimal(10,2) NOT NULL COMMENT 'Цена',
  `serviceName` varchar(30) NOT NULL COMMENT 'Название сервиса',
  PRIMARY KEY (`repairID`),
  UNIQUE KEY `repairID` (`repairID`,`carID`),
  KEY `carID` (`carID`),
  CONSTRAINT `Repairs_ibfk_1` FOREIGN KEY (`carID`) REFERENCES `Cars` (`CarID`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Ремонт';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Repairs`
--

LOCK TABLES `Repairs` WRITE;
/*!40000 ALTER TABLE `Repairs` DISABLE KEYS */;
INSERT INTO `Repairs` VALUES
(1,'engine','critical','completed','2026-01-15',20,'2025-08-10','Поломка турбины','Замена турбокомпрессора и ремонт системы смазки',125000.00,'Автотехцентр Турбо'),
(2,'engine','high','in_progress',NULL,6,'2025-09-14','Потеря мощности','Диагностика и ремонт системы впрыска топлива',45000.00,'Дизель Сервис'),
(3,'engine','high','planned',NULL,15,'2025-09-15','Перегрев двигателя','Замена радиатора и термостата',28000.00,'Автохолод'),
(4,'transmission','critical','completed','2026-02-20',5,'2025-07-15','Шум в коробке передач','Капитальный ремонт АКПП, замена фрикционов',89000.00,'Трансмиссионный центр'),
(5,'transmission','high','planned',NULL,20,'2025-09-12','Пробуксовка сцепления','Замена сцепления и выжимного подшипника',35000.00,'Сцепление Сервис'),
(6,'transmission','medium','completed','2025-12-01',8,'2025-08-25','Затрудненное переключение','Замена масла в КПП и регулировка',12000.00,'Автотехсервис'),
(7,'transmission','low','planned',NULL,12,'2025-10-10','Профилактика','Плановое обслуживание коробки передач',8000.00,'Трансмиссия Профи'),
(8,'brakes','high','completed','2025-11-30',1,'2025-09-14','Износ тормозных дисков','Замена передних тормозных дисков и колодок',18500.00,'Тормозной центр'),
(9,'brakes','medium','completed','2025-10-15',3,'2025-08-20','Проверка тормозной системы','Диагностика и замена тормозной жидкости',7500.00,'Автобезопасность'),
(10,'brakes','high','in_progress',NULL,18,'2025-09-13','Вибрация при торможении','Проточка тормозных дисков и замена колодок',14200.00,'Тормозной мастер'),
(11,'brakes','medium','planned',NULL,22,'2025-09-25','Плановое обслуживание','Замена задних тормозных колодок',9200.00,'Сервис Тормозов'),
(12,'brakes','critical','completed','2026-01-10',25,'2025-07-30','Отказ тормозной системы','Полная диагностика и ремонт тормозной системы',31500.00,'Экстренный ремонт'),
(13,'electrical','medium','completed','2025-10-20',7,'2025-08-05','Проблемы с запуском','Замена стартера и диагностика электропроводки',16800.00,'Автоэлектрик'),
(14,'electrical','high','completed','2026-03-15',11,'2025-09-10','Неисправность генератора','Замена генератора и регулятора напряжения',23400.00,'Электро Сервис'),
(15,'electrical','medium','in_progress',NULL,16,'2025-09-14','Проблемы с освещением','Диагностика и ремонт цепи освещения',8900.00,'Свет и Электрика'),
(16,'electrical','low','completed','2025-09-30',21,'2025-09-01','Не работает кондиционер','Заправка кондиционера и диагностика',6700.00,'Климат Контроль'),
(17,'electrical','high','planned',NULL,26,'2025-10-05','Нестабильная работа приборов','Диагностика электронных блоков управления',15600.00,'Электро Диагност'),
(18,'body','medium','completed','2025-12-25',2,'2025-07-22','Незначительное ДТП','Ремонт переднего бампера и покраска',42700.00,'Кузовный цех'),
(19,'body','low','completed','2025-10-10',9,'2025-08-18','Коррозия кузова','Антикоррозийная обработка и локальный ремонт',28900.00,'Антикоррозийный центр'),
(20,'body','high','in_progress',NULL,13,'2025-09-13','Повреждение двери','Ремонт и замена дверной панели',53800.00,'Кузовной мастер'),
(21,'body','medium','planned',NULL,19,'2025-09-28','Царапины на кузове','Полировка и локальная покраска',18700.00,'Автоэстетика'),
(22,'other','medium','completed','2025-11-15',4,'2025-08-12','Износ подвески','Замена амортизаторов и сайлентблоков',32400.00,'Подвеска Сервис'),
(23,'other','high','completed','2026-02-28',10,'2025-09-05','Течь рулевой рейки','Ремонт рулевой рейки и замена сальников',41800.00,'Рулевой мастер'),
(24,'other','critical','completed','2026-04-10',14,'2025-07-28','Разрыв топливного шланга','Замена топливных магистралей и диагностика',27600.00,'Топливные системы'),
(25,'other','low','cancelled',NULL,17,'2025-09-10','Плановый осмотр','Осмотр отменен по техническим причинам',0.00,'Техосмотр Сервис'),
(26,'body','low','completed','2026-10-07',12,'2025-10-07','Ржавчина','Очистка кузова от ржавчины и точечная покраска мест ремонта',15000.00,'Антикор Сервис');
/*!40000 ALTER TABLE `Repairs` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER after_repair_insert 
AFTER INSERT ON Repairs
FOR EACH ROW
BEGIN
    IF NEW.status = 'in_progress' THEN
        UPDATE Cars SET status = 'Maintenance' WHERE CarID = NEW.carID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`Schlegel`@`%`*/ /*!50003 TRIGGER after_repair_status_update 
AFTER UPDATE ON Repairs
FOR EACH ROW
BEGIN
    IF NEW.status = 'in_progress' AND OLD.status != 'in_progress' THEN
        UPDATE Cars SET status = 'Maintenance' WHERE CarID = NEW.carID;
    END IF;
    
    IF (NEW.status = 'completed' OR NEW.status = 'cancelled') AND OLD.status = 'in_progress' THEN
        UPDATE Cars SET status = 'Active' WHERE CarID = NEW.carID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `userID` int(5) NOT NULL AUTO_INCREMENT COMMENT 'ID пользователь',
  `username` varchar(30) NOT NULL COMMENT 'Логин',
  `passwordHash` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Пароль',
  `fullName` varchar(30) NOT NULL COMMENT 'Полное имя',
  `mail` varchar(30) NOT NULL COMMENT 'Почта',
  `phone` varchar(20) DEFAULT NULL COMMENT 'Телефон',
  `role` enum('admin','mechanic','manager') NOT NULL COMMENT 'Роль',
  `passwordDate` datetime NOT NULL COMMENT 'Дата последней смены пароля',
  `isBlocked` enum('true','false') NOT NULL COMMENT 'Заблокирован ли пользователь',
  `loginAttempts` int(1) DEFAULT 0 COMMENT 'Количество неудачных попыток входа',
  `lastLoginAttempt` timestamp NULL DEFAULT NULL COMMENT 'Время последней попытки входа',
  `blockedUntil` datetime DEFAULT NULL COMMENT 'Время окончания временной блокировки',
  PRIMARY KEY (`userID`),
  UNIQUE KEY `userID` (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Пользователи';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES
(1,'admin','21232f297a57a5a743894a0e4a801fc3','Супер Пупер Админ','shlegelza14@gmail.com','89236047765','admin','2025-09-10 00:00:00','false',0,NULL,NULL),
(2,'ivanov_p','6d444b6efeeef91bc2c422d399a79890','Иванов Пётр Сергеевич','p.ivanov@example.ru',NULL,'mechanic','2025-09-15 00:00:00','false',0,NULL,NULL),
(3,'sidorov_a','cc03e747a6afbbcbf8be7668acfebee5','Сидоров Алексей Владимирович','a.sidorov@example.ru',NULL,'mechanic','2025-09-15 00:00:00','false',0,NULL,NULL),
(4,'petrov_m','e99a18c428cb38d5f260853678922e03','Петров Михаил Иванович','m.petrov@example.ru',NULL,'mechanic','2025-09-15 00:00:00','false',0,NULL,NULL),
(5,'kozlov_d','5f4dcc3b5aa765d61d8327deb882cf99','Козлов Дмитрий Николаевич','d.kozlov@example.ru',NULL,'mechanic','2025-09-15 00:00:00','true',5,'2025-10-02 10:14:15',NULL),
(6,'smirnova_o','777a9cc4a183bca929313b477a8b69b7','Смирнова Ольга Викторовна','o.smirnova@example.ru',NULL,'manager','2025-09-15 00:00:00','true',0,NULL,NULL),
(7,'popova_e','6c82452e093c04782e96e2b44a434cd2','Попова Екатерина Александровна','e.popova@example.ru',NULL,'manager','2025-09-15 00:00:00','false',0,NULL,NULL);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'project_Schlegel'
--
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetCarHistoryReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
DELIMITER ;;
CREATE DEFINER=`Schlegel`@`%` PROCEDURE `GetCarHistoryReport`(
    IN p_car_id INT,
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN
    -- Объединяем данные о ТО и ремонте для конкретного автомобиля
    SELECT
        'Maintenance' AS record_type,
        m.maintenanceID AS id,
        mt.name AS type_name,
        m.priority,
        m.status,
        m.startDate AS date_start,
        m.completeDate AS date_end,
        m.totalCost AS cost,
        u.fullName AS mechanic_name,
        m.description
    FROM Maintenance m
    JOIN MaintenanceTypes mt ON m.typeID = mt.typeID
    JOIN Users u ON m.userID = u.userID
    WHERE m.carID = p_car_id
      AND (m.startDate >= p_date_from OR p_date_from IS NULL)
      AND (m.completeDate <= p_date_to OR p_date_to IS NULL)

    UNION ALL

    SELECT
        'Repair' AS record_type,
        r.repairID AS id,
        r.repairType AS type_name,
        r.priority,
        r.status,
        r.date AS date_start,
        r.date AS date_end,
        r.cost,
        '' AS mechanic_name, -- Заменяем на пустую строку
        r.description
    FROM Repairs r
    WHERE r.carID = p_car_id
      AND (r.date >= p_date_from OR p_date_from IS NULL)
      AND (r.date <= p_date_to OR p_date_to IS NULL)

    ORDER BY date_start DESC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetCostsByPeriodMonthlyReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
DELIMITER ;;
CREATE DEFINER=`Schlegel`@`%` PROCEDURE `GetCostsByPeriodMonthlyReport`(
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN

    -- Создаём временную таблицу для хранения месяцев
    DROP TEMPORARY TABLE IF EXISTS temp_months;
    CREATE TEMPORARY TABLE temp_months (
        month_year VARCHAR(7), -- Формат 'YYYY-MM'
        month_start DATE,
        month_end DATE
    );

    -- Заполняем временную таблицу месяцами в заданном периоде
    SET @current_date = p_date_from;
    WHILE @current_date <= p_date_to DO
        INSERT INTO temp_months (month_year, month_start, month_end)
        VALUES (
            DATE_FORMAT(@current_date, '%Y-%m'),
            @current_date,
            LAST_DAY(@current_date)
        );
        SET @current_date = DATE_ADD(@current_date, INTERVAL 1 MONTH);
    END WHILE;

    -- Получаем данные по месяцам для Maintenance и Repairs
    SELECT 
        'Maintenance' AS category,
        SUM(CASE WHEN tm.month_year = DATE_FORMAT(m.startDate, '%Y-%m') THEN m.totalCost ELSE 0 END) AS total_cost,
        tm.month_year
    FROM 
        temp_months tm
    LEFT JOIN 
        Maintenance m ON m.startDate BETWEEN tm.month_start AND tm.month_end
    GROUP BY 
        tm.month_year

    UNION ALL

    SELECT 
        'Repairs' AS category,
        SUM(CASE WHEN tm.month_year = DATE_FORMAT(r.date, '%Y-%m') THEN r.cost ELSE 0 END) AS total_cost,
        tm.month_year
    FROM 
        temp_months tm
    LEFT JOIN 
        Repairs r ON r.date BETWEEN tm.month_start AND tm.month_end
    GROUP BY 
        tm.month_year

    ORDER BY 
        category ASC, month_year ASC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetFleetSummaryReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
DELIMITER ;;
CREATE DEFINER=`Schlegel`@`%` PROCEDURE `GetFleetSummaryReport`()
BEGIN

    -- 1. Общие метрики (сводка)
    SELECT 
        'summary' AS section_type,
        (SELECT COUNT(*) FROM Cars) AS total_cars,
        COALESCE(
            AVG(mileage),
            0.0
        ) AS avg_mileage,
        COALESCE(
            AVG(maintenanceInterval),
            0.0
        ) AS avg_maintenance_interval,
        NULL AS status_name,
        NULL AS status_count,
        NULL AS brand_name,
        NULL AS brand_count,
        NULL AS car_model,
        NULL AS model_count,
        NULL AS model_avg_mileage,
        NULL AS model_avg_maintenance_interval
    FROM 
        Cars
    WHERE 
        mileage IS NOT NULL AND maintenanceInterval IS NOT NULL
    UNION ALL
    -- 2. Данные по статусам
    SELECT 
        'status' AS section_type,
        NULL AS total_cars,
        NULL AS avg_mileage,
        NULL AS avg_maintenance_interval,
        status AS status_name,
        COUNT(*) AS status_count,
        NULL AS brand_name,
        NULL AS brand_count,
        NULL AS car_model,
        NULL AS model_count,
        NULL AS model_avg_mileage,
        NULL AS model_avg_maintenance_interval
    FROM 
        Cars
    GROUP BY 
        status
    UNION ALL
    -- 3. Данные по брендам
    SELECT 
        'brand' AS section_type,
        NULL AS total_cars,
        NULL AS avg_mileage,
        NULL AS avg_maintenance_interval,
        NULL AS status_name,
        NULL AS status_count,
        brand AS brand_name,
        COUNT(*) AS brand_count,
        NULL AS car_model,
        NULL AS model_count,
        COALESCE(
            AVG(mileage),
            0.0
        ) AS model_avg_mileage,
        COALESCE(
            AVG(maintenanceInterval),
            0.0
        ) AS model_avg_maintenance_interval
    FROM 
        Cars
    WHERE 
        mileage IS NOT NULL AND maintenanceInterval IS NOT NULL
    GROUP BY 
        brand
    UNION ALL
    -- 4. Данные по моделям
    SELECT 
        'model' AS section_type,
        NULL AS total_cars,
        NULL AS avg_mileage,
        NULL AS avg_maintenance_interval,
        NULL AS status_name,
        NULL AS status_count,
        NULL AS brand_name,
        NULL AS brand_count,
        CONCAT(brand, ' ', model) AS car_model,
        COUNT(*) AS model_count,
        COALESCE(
            AVG(mileage),
            0.0
        ) AS model_avg_mileage,
        COALESCE(
            AVG(maintenanceInterval),
            0.0
        ) AS model_avg_maintenance_interval
    FROM 
        Cars
    WHERE 
        mileage IS NOT NULL AND maintenanceInterval IS NOT NULL
    GROUP BY 
        brand, model
    ORDER BY 
        section_type ASC, 
        CASE WHEN section_type = 'model' THEN model_count ELSE 0 END DESC,
        CASE WHEN section_type = 'brand' THEN brand_count ELSE 0 END DESC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetMaintenanceLogReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
DELIMITER ;;
CREATE DEFINER=`Schlegel`@`%` PROCEDURE `GetMaintenanceLogReport`(
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN

    SELECT 
        'ТО' AS record_type, -- Замена 'Maintenance' на 'ТО'
        m.maintenanceID AS id,
        CONCAT(c.brand, ' ', c.model, ' (', c.licensePlate, ')') AS car_info,
        m.startDate AS date,
        mt.name AS type_name, -- Используем name из MaintenanceTypes (уже русское)
        m.totalCost AS cost,
        u.fullName AS mechanic_name,
        m.description,
        CASE 
            WHEN m.status = 'planned' THEN 'Запланировано'
            WHEN m.status = 'in_progress' THEN 'В процессе'
            WHEN m.status = 'completed' THEN 'Выполнено'
            WHEN m.status = 'cancelled' THEN 'Отменено'
            WHEN m.status = 'on_hold' THEN 'На паузе'
            ELSE m.status
        END AS status
    FROM 
        Maintenance m
    JOIN 
        Cars c ON m.carID = c.CarID
    JOIN 
        MaintenanceTypes mt ON m.typeID = mt.typeID
    LEFT JOIN 
        Users u ON m.userID = u.userID
    WHERE 
        m.startDate BETWEEN p_date_from AND p_date_to

    UNION ALL

    SELECT 
        'Ремонт' AS record_type, -- Замена 'Repairs' на 'Ремонт'
        r.repairID AS id,
        CONCAT(c.brand, ' ', c.model, ' (', c.licensePlate, ')') AS car_info,
        r.date AS date,
        CASE 
            WHEN r.repairType = 'engine' THEN 'Двигатель'
            WHEN r.repairType = 'transmission' THEN 'Трансмиссия'
            WHEN r.repairType = 'brakes' THEN 'Тормоза'
            WHEN r.repairType = 'electrical' THEN 'Электрика'
            WHEN r.repairType = 'body' THEN 'Кузов'
            WHEN r.repairType = 'other' THEN 'Прочее'
            ELSE r.repairType
        END AS type_name, -- Локализация типов ремонтов
        r.cost AS cost,
        'Внешний сервис' AS mechanic_name, -- Более понятное название вместо 'External Service'
        r.description,
        CASE 
            WHEN r.status = 'planned' THEN 'Запланировано'
            WHEN r.status = 'in_progress' THEN 'В процессе'
            WHEN r.status = 'completed' THEN 'Выполнено'
            WHEN r.status = 'cancelled' THEN 'Отменено'
            ELSE r.status
        END AS status -- Локализация статусов для ремонтов
    FROM 
        Repairs r
    JOIN 
        Cars c ON r.carID = c.CarID
    WHERE 
        r.date BETWEEN p_date_from AND p_date_to

    ORDER BY 
        date ASC, record_type ASC, car_info ASC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetMechanicPerformanceReport` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
DELIMITER ;;
CREATE DEFINER=`Schlegel`@`%` PROCEDURE `GetMechanicPerformanceReport`(
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN

    SELECT 
        u.userID AS mechanicID,
        u.fullName AS fullName,
        COALESCE(maint.maintenance_count, 0) AS total_works_count, -- Только работы из Maintenance
        COALESCE(maint.maintenance_cost, 0) AS total_cost          -- Только стоимость из Maintenance
    FROM 
        Users u
    LEFT JOIN (
        -- Подзапрос для подсчёта ТО
        SELECT 
            userID,
            COUNT(*) AS maintenance_count,
            SUM(totalCost) AS maintenance_cost
        FROM 
            Maintenance
        WHERE 
            startDate BETWEEN p_date_from AND p_date_to
        GROUP BY 
            userID
    ) maint ON u.userID = maint.userID
    WHERE 
        u.role = 'mechanic'
        AND u.isBlocked = 'false'
    ORDER BY 
        total_cost DESC, fullName ASC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-29 11:38:41
