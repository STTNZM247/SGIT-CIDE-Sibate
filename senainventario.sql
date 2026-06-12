-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: invsena
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

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
-- Current Database: `invsena`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `invsena` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `invsena`;

--
-- Table structure for table `auditoria_log`
--

DROP TABLE IF EXISTS `auditoria_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auditoria_log` (
  `id_log` int(11) NOT NULL AUTO_INCREMENT,
  `accion` varchar(30) NOT NULL,
  `entidad` varchar(80) NOT NULL,
  `entidad_id` varchar(80) DEFAULT NULL,
  `descripcion` longtext NOT NULL,
  `rol_usuario` varchar(80) DEFAULT NULL,
  `ip_origen` varchar(45) DEFAULT NULL,
  `fch_registro` datetime(6) NOT NULL,
  `id_usuario_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_log`),
  KEY `auditoria_log_id_usuario_fk_524aafda_fk_usuario_id_usu` (`id_usuario_fk`),
  CONSTRAINT `auditoria_log_id_usuario_fk_524aafda_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria_log`
--

LOCK TABLES `auditoria_log` WRITE;
/*!40000 ALTER TABLE `auditoria_log` DISABLE KEYS */;
INSERT INTO `auditoria_log` VALUES (1,'crear','producto','12','Se creó el producto \"COSO\".','admin','127.0.0.1','2026-04-13 20:10:39.344334',1),(2,'crear','pedido','12','Usuario creó el pedido #12. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-04-13 20:34:46.733751',3),(3,'crear','pedido','13','Usuario creó el pedido #13. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-04-13 20:47:55.292475',3),(4,'crear','pedido','14','Usuario creó el pedido #14. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-04-13 20:48:11.570083',3),(5,'actualizar','pedido','12','Pedido #12 fue cancelado/rechazado por personal de almacén. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-13 21:03:07.607945',1),(6,'actualizar','pedido','13','Pedido #13 fue cancelado/rechazado por personal de almacén. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-13 21:21:34.604829',1),(7,'actualizar','pedido','14','Pedido #14 cancelado automáticamente por vencimiento en estado pendiente. | Actor: sistema',NULL,NULL,'2026-04-13 21:30:37.657887',NULL),(8,'actualizar','usuario','3','Se dejó desactivado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:30.404217',1),(9,'actualizar','usuario','3','Se dejó activado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:31.540141',1),(10,'actualizar','usuario','3','Se dejó desactivado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:33.489577',1),(11,'actualizar','usuario','3','Se dejó activado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:35.327210',1),(12,'actualizar','usuario','3','Se dejó desactivado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:36.225176',1),(13,'actualizar','usuario','3','Se dejó activado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 19:58:36.834139',1),(14,'actualizar','usuario','4','Se dejó desactivado el acceso del usuario ejemplo@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 20:01:06.673915',1),(15,'actualizar','usuario','4','Se dejó activado el acceso del usuario ejemplo@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 20:05:35.926659',1),(16,'actualizar','usuario','3','Se dejó desactivado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 20:05:37.362596',1),(17,'actualizar','usuario','3','Se dejó activado el acceso del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-14 20:41:13.948071',1),(18,'actualizar','usuario','5','Se envió enlace manual de validación SENA al usuario sttn247@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-04-23 16:29:00.356851',1),(19,'actualizar','usuario','3','Se envió enlace manual de validación SENA al usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-06 18:20:04.788957',1),(20,'crear','producto','13','Se creó el producto \"CABLE\" (Consumo, unidad: Rollo, ubicación: electricidad). | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-14 23:04:24.124606',1),(21,'actualizar','inventario_importacion','excel','Productos procesados: 10. Creados: 0. Actualizados: 10. Imágenes principales: 10. Imágenes secundarias: 0. Errores: 0. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-21 22:31:19.323325',1),(22,'actualizar','inventario_importacion','excel','Productos procesados: 73. Creados: 73. Actualizados: 0. Imágenes principales: 73. Imágenes secundarias: 1. Errores: 0. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 21:26:02.505812',1),(23,'crear','subcategoria','22','Se creó la subcategoría \"tmp_audit_root\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta: tmp_audit_root. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:12.265830',1),(24,'actualizar','subcategoria','22','Se renombró subcategoría de \"tmp_audit_root\" a \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta anterior: tmp_audit_root. Ruta nueva: tmp_audit_root_ren. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:12.274671',1),(25,'actualizar','producto','91','Se movió producto \"tmp_audit_prod\" a subcategoría \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta destino: tmp_audit_root_ren. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:12.287045',1),(26,'actualizar','producto','91','Se restauró (Ctrl+Z) producto \"tmp_audit_prod\" a raíz del catálogo \"MAQUINARIA DE CONSTRUCCION\". IDs anteriores: [22]. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:12.294723',1),(27,'eliminar','subcategoria','22','Se eliminó subcategoría \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta eliminada: tmp_audit_root_ren. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:12.309379',1),(28,'crear','subcategoria','23','Se creó la subcategoría \"tmp_audit_root\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta: tmp_audit_root. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:41.523288',1),(29,'actualizar','subcategoria','23','Se renombró subcategoría de \"tmp_audit_root\" a \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta anterior: tmp_audit_root. Ruta nueva: tmp_audit_root_ren. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:41.532781',1),(30,'actualizar','producto','92','Se movió producto \"tmp_audit_prod\" a subcategoría \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta destino: tmp_audit_root_ren. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:41.545977',1),(31,'actualizar','producto','92','Se restauró (Ctrl+Z) producto \"tmp_audit_prod\" a raíz del catálogo \"MAQUINARIA DE CONSTRUCCION\". IDs anteriores: [23]. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:41.557448',1),(32,'eliminar','subcategoria','23','Se eliminó subcategoría \"tmp_audit_root_ren\" en catálogo \"MAQUINARIA DE CONSTRUCCION\". Ruta eliminada: tmp_audit_root_ren. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:20:41.576275',1),(33,'crear','subcategoria','26','Se creó la subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta: guantes. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:18.433053',1),(34,'actualizar','producto','23','Se movió producto \"GUANTES CARNAZA AZUL\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:21.013631',1),(35,'actualizar','producto','24','Se movió producto \"GUANTES DE CARNAZA AMARILLO LARGO\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:24.598416',1),(36,'actualizar','producto','25','Se movió producto \"GUANTES DE CARNAZA AMARILO PEQUEÑO\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:25.911031',1),(37,'actualizar','producto','26','Se movió producto \"GUANTES DE CARNAZA IMPERMEABLE\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:27.087361',1),(38,'actualizar','producto','29','Se movió producto \"GUANTES MULTIFLEX\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:29.005857',1),(39,'actualizar','producto','28','Se movió producto \"GUANTES DE TRABAJO TELA CON PUNTOS ANTIDESLIZANTES\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:30.601771',1),(40,'actualizar','producto','27','Se movió producto \"GUANTES DE CARNZA\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:31.778022',1),(41,'actualizar','producto','31','Se movió producto \"GUANTES VAQUETA\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:33.774960',1),(42,'actualizar','producto','30','Se movió producto \"GUANTES QUIRURGICOS\" a subcategoría \"guantes\" en catálogo \"E.P.P\". Ruta destino: guantes. Subcategorías anteriores: ninguna. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:41:37.990809',1),(43,'crear','subcategoria','27','Se creó la subcategoría \"cuero\" en catálogo \"E.P.P\". Ruta: guantes / cuero. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:12.718986',1),(44,'crear','subcategoria','28','Se creó la subcategoría \"desechables\" en catálogo \"E.P.P\". Ruta: guantes / desechables. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:21.699759',1),(45,'actualizar','producto','24','Se movió producto \"GUANTES DE CARNAZA AMARILLO LARGO\" a subcategoría \"cuero\" en catálogo \"E.P.P\". Ruta destino: guantes / cuero. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:25.183809',1),(46,'actualizar','producto','25','Se movió producto \"GUANTES DE CARNAZA AMARILO PEQUEÑO\" a subcategoría \"cuero\" en catálogo \"E.P.P\". Ruta destino: guantes / cuero. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:27.254541',1),(47,'actualizar','producto','26','Se movió producto \"GUANTES DE CARNAZA IMPERMEABLE\" a subcategoría \"cuero\" en catálogo \"E.P.P\". Ruta destino: guantes / cuero. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:29.122737',1),(48,'actualizar','producto','30','Se movió producto \"GUANTES QUIRURGICOS\" a subcategoría \"desechables\" en catálogo \"E.P.P\". Ruta destino: guantes / desechables. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:32.701491',1),(49,'actualizar','producto','31','Se movió producto \"GUANTES VAQUETA\" a subcategoría \"cuero\" en catálogo \"E.P.P\". Ruta destino: guantes / cuero. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:35.923969',1),(50,'crear','subcategoria','29','Se creó la subcategoría \"guantes de electricidad\" en catálogo \"E.P.P\". Ruta: guantes / guantes de electricidad. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:44.835486',1),(51,'actualizar','producto','29','Se movió producto \"GUANTES MULTIFLEX\" a subcategoría \"guantes de electricidad\" en catálogo \"E.P.P\". Ruta destino: guantes / guantes de electricidad. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:49.280007',1),(52,'actualizar','producto','28','Se movió producto \"GUANTES DE TRABAJO TELA CON PUNTOS ANTIDESLIZANTES\" a subcategoría \"guantes de electricidad\" en catálogo \"E.P.P\". Ruta destino: guantes / guantes de electricidad. Subcategorías anteriores: guantes. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-22 23:42:50.920567',1),(53,'crear','subcategoria','30','Se creó la subcategoría \"destornilladores\" en catálogo \"ELECTRICO\". Ruta: destornilladores. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-23 01:04:15.405578',1),(54,'eliminar','subcategoria','30','Se eliminó subcategoría \"destornilladores\" en catálogo \"ELECTRICO\". Ruta eliminada: destornilladores. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-23 01:13:20.767669',1),(55,'crear','subcategoria','31','Se creó la subcategoría \"destornillador\" en catálogo \"ELECTRICO\". Ruta: destornillador. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-23 01:13:27.748333',1),(56,'actualizar','usuario','3','Se aprobó manualmente la validación SENA del usuario alex@gmail.com. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-28 13:38:45.564790',1),(57,'crear','pedido','15','Usuario creó el pedido #15. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-05-29 20:42:03.714170',3),(58,'actualizar','pedido','15','Pedido #15 fue rechazado por personal de almacén. Motivo: El pedido fue rechazado por no disponibilidad. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-29 22:09:28.529419',1),(59,'crear','pedido','16','Usuario creó el pedido #16. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-05-29 22:12:46.973657',3),(60,'actualizar','pedido','16','Pedido #16 pasó a esperando entrega. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-29 22:13:36.216702',1),(61,'crear','subcategoria','32','Se creó la subcategoría \"hola\" en catálogo \"ASEO\". Ruta: cabeza / hola. Nodos creados: 1. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-29 23:43:04.660515',1),(62,'actualizar','pedido','16','Pedido #16 fue confirmado como entregado en almacén. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-30 00:21:03.310296',1),(63,'crear','pedido','17','Usuario creó el pedido #17. | Actor: alex zea (usuario)','usuario','127.0.0.1','2026-05-30 00:21:46.177537',3),(64,'crear','ubicacion_producto','1','Se creó la ubicación \"ELECTRICIDAD\". | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-30 01:11:10.444042',1),(65,'actualizar','pedido','17','Pedido #17 pasó a esperando entrega. | Actor: Johan zea (admin)','admin','127.0.0.1','2026-05-30 01:19:24.720637',1);
/*!40000 ALTER TABLE `auditoria_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auditorio`
--

DROP TABLE IF EXISTS `auditorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auditorio` (
  `id_aud` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_auditorio` varchar(255) DEFAULT NULL,
  `descripcion` longtext DEFAULT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_usu_cat_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_aud`),
  KEY `auditorio_id_usu_cat_fk_cfcf81ee_fk_usu_cat_id_usu_cat` (`id_usu_cat_fk`),
  CONSTRAINT `auditorio_id_usu_cat_fk_cfcf81ee_fk_usu_cat_id_usu_cat` FOREIGN KEY (`id_usu_cat_fk`) REFERENCES `usu_cat` (`id_usu_cat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditorio`
--

LOCK TABLES `auditorio` WRITE;
/*!40000 ALTER TABLE `auditorio` DISABLE KEYS */;
/*!40000 ALTER TABLE `auditorio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add usuario',6,'add_usuario'),(22,'Can change usuario',6,'change_usuario'),(23,'Can delete usuario',6,'delete_usuario'),(24,'Can view usuario',6,'view_usuario'),(25,'Can add catalogo',7,'add_catalogo'),(26,'Can change catalogo',7,'change_catalogo'),(27,'Can delete catalogo',7,'delete_catalogo'),(28,'Can view catalogo',7,'view_catalogo'),(29,'Can add rol',8,'add_rol'),(30,'Can change rol',8,'change_rol'),(31,'Can delete rol',8,'delete_rol'),(32,'Can view rol',8,'view_rol'),(33,'Can add usu cat',9,'add_usucat'),(34,'Can change usu cat',9,'change_usucat'),(35,'Can delete usu cat',9,'delete_usucat'),(36,'Can view usu cat',9,'view_usucat'),(37,'Can add producto',10,'add_producto'),(38,'Can change producto',10,'change_producto'),(39,'Can delete producto',10,'delete_producto'),(40,'Can view producto',10,'view_producto'),(41,'Can add disponibilidad',11,'add_disponibilidad'),(42,'Can change disponibilidad',11,'change_disponibilidad'),(43,'Can delete disponibilidad',11,'delete_disponibilidad'),(44,'Can view disponibilidad',11,'view_disponibilidad'),(45,'Can add auditorio',12,'add_auditorio'),(46,'Can change auditorio',12,'change_auditorio'),(47,'Can delete auditorio',12,'delete_auditorio'),(48,'Can view auditorio',12,'view_auditorio'),(49,'Can add detalle pedido',13,'add_detallepedido'),(50,'Can change detalle pedido',13,'change_detallepedido'),(51,'Can delete detalle pedido',13,'delete_detallepedido'),(52,'Can view detalle pedido',13,'view_detallepedido'),(53,'Can add pedido',14,'add_pedido'),(54,'Can change pedido',14,'change_pedido'),(55,'Can delete pedido',14,'delete_pedido'),(56,'Can view pedido',14,'view_pedido'),(57,'Can add carrito item',15,'add_carritoitem'),(58,'Can change carrito item',15,'change_carritoitem'),(59,'Can delete carrito item',15,'delete_carritoitem'),(60,'Can view carrito item',15,'view_carritoitem'),(61,'Can add pedido evidencia',16,'add_pedidoevidencia'),(62,'Can change pedido evidencia',16,'change_pedidoevidencia'),(63,'Can delete pedido evidencia',16,'delete_pedidoevidencia'),(64,'Can view pedido evidencia',16,'view_pedidoevidencia'),(65,'Can add notificacion',17,'add_notificacion'),(66,'Can change notificacion',17,'change_notificacion'),(67,'Can delete notificacion',17,'delete_notificacion'),(68,'Can view notificacion',17,'view_notificacion'),(69,'Can add auditoria log',18,'add_auditorialog'),(70,'Can change auditoria log',18,'change_auditorialog'),(71,'Can delete auditoria log',18,'delete_auditorialog'),(72,'Can view auditoria log',18,'view_auditorialog'),(73,'Can add password reset token',19,'add_passwordresettoken'),(74,'Can change password reset token',19,'change_passwordresettoken'),(75,'Can delete password reset token',19,'delete_passwordresettoken'),(76,'Can view password reset token',19,'view_passwordresettoken'),(77,'Can add tipo doc',20,'add_tipodoc'),(78,'Can change tipo doc',20,'change_tipodoc'),(79,'Can delete tipo doc',20,'delete_tipodoc'),(80,'Can view tipo doc',20,'view_tipodoc'),(81,'Can add verificacion sena token',21,'add_verificacionsenatoken'),(82,'Can change verificacion sena token',21,'change_verificacionsenatoken'),(83,'Can delete verificacion sena token',21,'delete_verificacionsenatoken'),(84,'Can view verificacion sena token',21,'view_verificacionsenatoken'),(85,'Can add producto foto',22,'add_productofoto'),(86,'Can change producto foto',22,'change_productofoto'),(87,'Can delete producto foto',22,'delete_productofoto'),(88,'Can view producto foto',22,'view_productofoto'),(89,'Can add subcategoria',23,'add_subcategoria'),(90,'Can change subcategoria',23,'change_subcategoria'),(91,'Can delete subcategoria',23,'delete_subcategoria'),(92,'Can view subcategoria',23,'view_subcategoria'),(93,'Can add importacion inventario log',24,'add_importacioninventariolog'),(94,'Can change importacion inventario log',24,'change_importacioninventariolog'),(95,'Can delete importacion inventario log',24,'delete_importacioninventariolog'),(96,'Can view importacion inventario log',24,'view_importacioninventariolog'),(97,'Can add ubicacion producto',25,'add_ubicacionproducto'),(98,'Can change ubicacion producto',25,'change_ubicacionproducto'),(99,'Can delete ubicacion producto',25,'delete_ubicacionproducto'),(100,'Can view ubicacion producto',25,'view_ubicacionproducto');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carrito_item`
--

DROP TABLE IF EXISTS `carrito_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carrito_item` (
  `id_carrito_item` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(10) unsigned NOT NULL CHECK (`cantidad` >= 0),
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_prod_fk` int(11) NOT NULL,
  `id_usuario_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_carrito_item`),
  UNIQUE KEY `uq_carrito_usuario_producto` (`id_usuario_fk`,`id_prod_fk`),
  KEY `carrito_item_id_prod_fk_1570e84f_fk_producto_id_prod` (`id_prod_fk`),
  CONSTRAINT `carrito_item_id_prod_fk_1570e84f_fk_producto_id_prod` FOREIGN KEY (`id_prod_fk`) REFERENCES `producto` (`id_prod`),
  CONSTRAINT `carrito_item_id_usuario_fk_bf98c22c_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carrito_item`
--

LOCK TABLES `carrito_item` WRITE;
/*!40000 ALTER TABLE `carrito_item` DISABLE KEYS */;
INSERT INTO `carrito_item` VALUES (35,1,'2026-04-21 19:53:50.349107','2026-04-21 19:53:50.349107',9,5);
/*!40000 ALTER TABLE `carrito_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo`
--

DROP TABLE IF EXISTS `catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalogo` (
  `id_cat` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_catalogo` varchar(255) DEFAULT NULL,
  `descripcion` longtext DEFAULT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_ubicacion_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_cat`),
  KEY `catalogo_id_ubicacion_fk_9ae08ab7_fk_ubicacion` (`id_ubicacion_fk`),
  CONSTRAINT `catalogo_id_ubicacion_fk_9ae08ab7_fk_ubicacion` FOREIGN KEY (`id_ubicacion_fk`) REFERENCES `ubicacion_producto` (`id_ubicacion`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo`
--

LOCK TABLES `catalogo` WRITE;
/*!40000 ALTER TABLE `catalogo` DISABLE KEYS */;
INSERT INTO `catalogo` VALUES (2,'MAQUINARIA DE CONSTRUCCION','materiales y elementos de construccion','2026-03-17 19:42:08.006615','2026-03-17 19:42:08.006618',NULL),(3,'ELECTRICO','materiales u objetos electricos','2026-03-17 20:40:36.691040','2026-03-17 20:40:36.691044',NULL),(4,'ASEO','catalogo aseo','2026-03-18 01:45:51.136122','2026-03-18 01:45:51.136129',NULL),(6,'EJEMPLO','este es el ejemplo','2026-03-31 16:06:56.298579','2026-03-31 16:06:56.298582',NULL),(7,'CONSTRUCCIÓN',NULL,'2026-05-22 21:25:53.837595','2026-05-22 21:25:53.837602',NULL),(8,'E.P.P',NULL,'2026-05-22 21:25:54.549238','2026-05-22 21:25:54.549240',NULL),(9,'PC CNC',NULL,'2026-05-22 21:25:58.423352','2026-05-22 21:25:58.423354',NULL),(10,'PC ELECTRICIDAD',NULL,'2026-05-22 21:25:59.670471','2026-05-22 21:25:59.670475',NULL);
/*!40000 ALTER TABLE `catalogo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_pedido`
--

DROP TABLE IF EXISTS `detalle_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalle_pedido` (
  `id_det_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(255) NOT NULL,
  `nombre_catalogo` varchar(255) DEFAULT NULL,
  `cantidad_solicitada` int(10) unsigned NOT NULL CHECK (`cantidad_solicitada` >= 0),
  `stock_referencia` int(11) DEFAULT NULL,
  `estado_detalle` varchar(50) NOT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_pedido_fk` int(11) NOT NULL,
  `id_prod_fk` int(11) DEFAULT NULL,
  `fecha_devolucion` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_det_pedido`),
  KEY `detalle_pedido_id_pedido_fk_30b9aca6_fk_pedido_id_pedido` (`id_pedido_fk`),
  KEY `detalle_pedido_id_prod_fk_83c1d706_fk_producto_id_prod` (`id_prod_fk`),
  CONSTRAINT `detalle_pedido_id_pedido_fk_30b9aca6_fk_pedido_id_pedido` FOREIGN KEY (`id_pedido_fk`) REFERENCES `pedido` (`id_pedido`),
  CONSTRAINT `detalle_pedido_id_prod_fk_83c1d706_fk_producto_id_prod` FOREIGN KEY (`id_prod_fk`) REFERENCES `producto` (`id_prod`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_pedido`
--

LOCK TABLES `detalle_pedido` WRITE;
/*!40000 ALTER TABLE `detalle_pedido` DISABLE KEYS */;
INSERT INTO `detalle_pedido` VALUES (1,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,12,'devuelto','2026-03-24 21:31:39.328583','2026-04-13 18:43:55.206868',1,9,NULL),(2,'TOMA CORRIENTE','ELECTRICO',20,70,'devuelto','2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',2,3,NULL),(3,'TAPABOCAS','ASEO',10,30,'devuelto','2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',2,5,NULL),(4,'DELIXI','MAQUINARIA DE CONSTRUCCION',1,20,'devuelto','2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',2,7,NULL),(5,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,30,'devuelto','2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',2,8,NULL),(6,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,11,'devuelto','2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',2,9,NULL),(7,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',2,10,'devuelto','2026-03-26 16:48:51.329570','2026-04-13 18:43:52.282793',3,9,NULL),(8,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',12,29,'devuelto','2026-03-26 16:48:51.329570','2026-04-13 18:43:52.282793',3,8,NULL),(9,'DELIXI','MAQUINARIA DE CONSTRUCCION',12,19,'devuelto','2026-03-26 16:48:51.329570','2026-04-13 18:43:52.282793',3,7,NULL),(10,'DELIXI','MAQUINARIA DE CONSTRUCCION',1,7,'devuelto','2026-03-26 17:18:00.347171','2026-04-13 18:43:50.479433',4,7,NULL),(11,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,17,'devuelto','2026-03-26 17:18:00.347171','2026-04-13 18:43:50.479433',4,8,NULL),(12,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,8,'devuelto','2026-03-26 17:18:00.347171','2026-04-13 18:43:50.479433',4,9,NULL),(13,'EJEMPLO','EJEMPLO',1,50,'devuelto','2026-03-31 16:10:59.624937','2026-04-13 18:43:44.596923',5,11,NULL),(14,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,16,'devuelto','2026-03-31 16:10:59.624937','2026-04-13 18:43:44.596923',5,8,NULL),(15,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,15,'devuelto','2026-04-08 20:55:43.582823','2026-04-13 18:40:47.748480',6,8,'2026-04-08 21:55:00.000000'),(16,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,7,'devuelto','2026-04-08 20:55:43.582823','2026-04-13 18:40:47.748480',6,9,'2026-04-08 21:55:00.000000'),(17,'DELIXI','MAQUINARIA DE CONSTRUCCION',1,6,'rechazado','2026-04-08 21:37:50.790430','2026-04-09 17:10:44.864192',7,7,'2026-04-08 22:37:00.000000'),(18,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,7,'rechazado','2026-04-08 21:37:50.790430','2026-04-09 17:10:44.864192',7,9,'2026-04-08 22:37:00.000000'),(19,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,14,'cancelado','2026-04-09 17:57:26.699845','2026-04-09 18:01:47.411955',8,8,'2026-04-09 13:10:00.000000'),(20,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,7,'cancelado','2026-04-09 17:57:26.699845','2026-04-09 18:01:47.411955',8,9,'2026-04-09 13:10:00.000000'),(21,'EJEMPLO','EJEMPLO',1,49,'devuelto','2026-04-09 18:03:51.731381','2026-04-13 18:41:20.147854',9,11,'2026-04-09 13:10:00.000000'),(22,'TAPABOCAS','ASEO',1,20,'devuelto','2026-04-11 00:10:47.225213','2026-04-13 18:41:29.413028',10,5,'2026-04-11 22:00:00.000000'),(23,'TOMA CORRIENTE','ELECTRICO',1,50,'devuelto','2026-04-11 00:10:47.225213','2026-04-13 18:41:29.413028',10,3,'2026-04-11 22:00:00.000000'),(24,'DELIXI','MAQUINARIA DE CONSTRUCCION',1,6,'devuelto','2026-04-11 00:10:47.225213','2026-04-13 18:41:29.413028',10,7,'2026-04-11 22:00:00.000000'),(25,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,30,'devuelto','2026-04-13 18:47:25.142309','2026-04-13 18:56:09.529573',11,8,'2026-04-13 14:00:00.000000'),(26,'DELIXI','MAQUINARIA DE CONSTRUCCION',1,20,'rechazado','2026-04-13 20:34:46.719464','2026-04-13 21:03:07.602617',12,7,'2026-04-13 20:40:00.000000'),(27,'COSO','EJEMPLO',1,4,'rechazado','2026-04-13 20:34:46.719464','2026-04-13 21:03:07.602617',12,12,'2026-04-13 20:40:00.000000'),(28,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,30,'rechazado','2026-04-13 20:34:46.719464','2026-04-13 21:03:07.602617',12,8,'2026-04-13 20:40:00.000000'),(29,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,12,'rechazado','2026-04-13 20:34:46.719464','2026-04-13 21:03:07.602617',12,9,'2026-04-13 20:40:00.000000'),(30,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,30,'rechazado','2026-04-13 20:47:55.282671','2026-04-13 21:21:34.600451',13,8,'2026-04-13 21:00:00.000000'),(31,'12 UND DESTORNILLADOR','MAQUINARIA DE CONSTRUCCION',1,12,'rechazado','2026-04-13 20:47:55.282671','2026-04-13 21:21:34.600451',13,9,'2026-04-13 21:00:00.000000'),(32,'COSO','EJEMPLO',1,4,'cancelado','2026-04-13 20:48:11.558101','2026-04-13 21:30:37.634181',14,12,'2026-04-13 21:05:00.000000'),(33,'CORTADOR DE TUBOS DE PVC','MAQUINARIA DE CONSTRUCCION',1,30,'cancelado','2026-04-13 20:48:11.558101','2026-04-13 21:30:37.634181',14,8,'2026-04-13 21:05:00.000000'),(34,'TAPABOCAS','E.P.P',1,92,'rechazado','2026-05-29 20:42:03.706361','2026-05-29 22:09:28.520992',15,39,NULL),(35,'GUANTES QUIRURGICOS','E.P.P',1,28,'rechazado','2026-05-29 20:42:03.706361','2026-05-29 22:09:28.520992',15,30,NULL),(36,'TAPABOCAS','E.P.P',4,92,'no_disponible','2026-05-29 22:12:46.962635','2026-05-29 22:13:36.206679',16,39,NULL),(37,'GUANTES QUIRURGICOS','E.P.P',3,28,'devuelto','2026-05-29 22:12:46.962635','2026-05-30 00:21:03.302871',16,30,NULL),(38,'GUANTES QUIRURGICOS','E.P.P',1,25,'esperando entrega','2026-05-30 00:21:46.164960','2026-05-30 01:19:24.702198',17,30,NULL);
/*!40000 ALTER TABLE `detalle_pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disponibilidad`
--

DROP TABLE IF EXISTS `disponibilidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disponibilidad` (
  `id_disp` int(11) NOT NULL AUTO_INCREMENT,
  `cantidad` int(11) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `descr_dispo` longtext DEFAULT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_prod_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_disp`),
  KEY `disponibilidad_id_prod_fk_b21b9f1e_fk_producto_id_prod` (`id_prod_fk`),
  CONSTRAINT `disponibilidad_id_prod_fk_b21b9f1e_fk_producto_id_prod` FOREIGN KEY (`id_prod_fk`) REFERENCES `producto` (`id_prod`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disponibilidad`
--

LOCK TABLES `disponibilidad` WRITE;
/*!40000 ALTER TABLE `disponibilidad` DISABLE KEYS */;
INSERT INTO `disponibilidad` VALUES (1,20,20,'20 PALAS MARCA TRUPER DE 72cm','2026-03-17 19:44:26.415860','2026-05-21 22:31:19.215060',2),(2,70,70,'70 toma corrientes Premium Montado','2026-03-17 20:43:19.856884','2026-05-21 22:31:18.586983',3),(3,80,80,'80 Mini Interruptor Inteligente Tuya Smartlife Switch Wifi Alex Blanco 16v','2026-03-17 21:05:13.488880','2026-05-21 22:31:18.494376',4),(4,30,30,'Lote X 15 Unds De Mascarilla Tapaboca Nitta N95 Ref. 9510-1','2026-03-18 01:46:57.333101','2026-05-28 16:15:21.605416',5),(6,20,20,'llave de tubo','2026-03-19 19:28:59.619934','2026-05-21 22:31:19.122537',7),(7,30,30,'Cortador de Tubos de PVC OuDiSi','2026-03-19 19:34:46.947587','2026-05-21 22:31:19.007325',8),(8,12,12,'destornilladores magnéticos amartisan','2026-03-19 19:36:23.604251','2026-05-21 22:31:18.713263',9),(10,50,50,'ejemplo','2026-03-31 16:07:43.375120','2026-05-21 22:31:17.935244',11),(11,4,4,'un coso de coso','2026-04-13 20:10:39.346333','2026-05-21 22:31:17.892164',12),(12,30,30,'','2026-05-14 23:04:24.126897','2026-05-21 22:31:18.474685',13),(13,14,15,'14','2026-05-22 21:25:53.845322','2026-05-22 21:25:53.845369',14),(14,24,24,'24','2026-05-22 21:25:54.107127','2026-05-22 21:25:54.107165',15),(15,3,3,'3','2026-05-22 21:25:54.158903','2026-05-22 21:25:54.158960',16),(16,8,8,'8','2026-05-22 21:25:54.198165','2026-05-22 21:25:54.198201',17),(17,5,5,'5','2026-05-22 21:25:54.230723','2026-05-22 21:25:54.230799',18),(18,5,5,'5','2026-05-22 21:25:54.305173','2026-05-22 21:25:54.305207',19),(19,8,8,'8','2026-05-22 21:25:54.330819','2026-05-22 21:25:54.330847',20),(20,4,4,'4','2026-05-22 21:25:54.422084','2026-05-22 21:25:54.422160',21),(21,8,8,'8','2026-05-22 21:25:54.483998','2026-05-22 21:25:54.484036',22),(22,8,8,'8','2026-05-22 21:25:54.553989','2026-05-22 21:25:54.554033',23),(23,32,32,'32','2026-05-22 21:25:54.569760','2026-05-22 21:25:54.569794',24),(24,10,10,'10','2026-05-22 21:25:54.592058','2026-05-22 21:25:54.592090',25),(25,10,10,'10','2026-05-22 21:25:54.716454','2026-05-22 21:25:54.716496',26),(26,60,60,'60','2026-05-22 21:25:54.730521','2026-05-22 21:25:54.730547',27),(27,36,36,'36','2026-05-22 21:25:54.742849','2026-05-22 21:25:54.742872',28),(28,20,20,'20','2026-05-22 21:25:54.827282','2026-05-22 21:25:54.827307',29),(29,24,24,'','2026-05-22 21:25:55.147461','2026-05-30 01:19:24.702198',30),(30,12,12,'12','2026-05-22 21:25:55.182049','2026-05-22 21:25:55.182102',31),(31,13,13,'13','2026-05-22 21:25:55.497164','2026-05-22 21:25:55.497242',32),(32,18,18,'18','2026-05-22 21:25:55.556000','2026-05-22 21:25:55.556086',33),(33,58,58,'58','2026-05-22 21:25:55.743845','2026-05-22 21:25:55.743871',34),(34,58,58,'58','2026-05-22 21:25:55.769163','2026-05-22 21:25:55.769188',35),(35,284,284,'284','2026-05-22 21:25:55.848730','2026-05-22 21:25:55.848751',36),(36,8,8,'8 cajas','2026-05-22 21:25:55.892539','2026-05-28 16:12:55.079286',37),(37,29,29,'29','2026-05-22 21:25:56.048236','2026-05-22 21:25:56.048263',38),(38,92,92,'92','2026-05-22 21:25:56.116080','2026-05-28 16:15:02.926764',39),(39,11,11,'11','2026-05-22 21:25:56.152464','2026-05-22 21:25:56.152486',40),(40,11,11,'11','2026-05-22 21:25:56.207396','2026-05-22 21:25:56.207429',41),(41,8,8,'8','2026-05-22 21:25:56.261455','2026-05-22 21:25:56.261479',42),(42,7,7,'7','2026-05-22 21:25:56.325011','2026-05-22 21:25:56.325049',43),(43,50,50,'50','2026-05-22 21:25:56.375484','2026-05-22 21:25:56.375512',44),(44,15,15,'15','2026-05-22 21:25:56.521535','2026-05-22 21:25:56.521564',45),(45,30,30,'30','2026-05-22 21:25:56.544310','2026-05-22 21:25:56.544350',46),(46,5,5,'5 rollos','2026-05-22 21:25:56.650119','2026-05-22 21:25:56.650147',47),(47,5,5,'5 rollos','2026-05-22 21:25:56.670518','2026-05-22 21:25:56.670551',48),(48,15,15,'15','2026-05-22 21:25:56.932017','2026-05-22 21:25:56.932046',49),(49,15,15,'15','2026-05-22 21:25:57.012067','2026-05-22 21:25:57.012097',50),(50,8,8,'8','2026-05-22 21:25:57.089161','2026-05-22 21:25:57.089199',51),(51,6,6,'6','2026-05-22 21:25:57.181130','2026-05-22 21:25:57.181153',52),(52,12,12,'12','2026-05-22 21:25:57.267672','2026-05-22 21:25:57.267707',53),(53,24,24,'24','2026-05-22 21:25:57.377078','2026-05-22 21:25:57.377138',54),(54,10,10,'10','2026-05-22 21:25:57.458130','2026-05-22 21:25:57.458152',55),(55,6,8,'6','2026-05-22 21:25:57.471253','2026-05-22 21:25:57.471278',56),(56,5,5,'5','2026-05-22 21:25:57.519297','2026-05-22 21:25:57.519320',57),(57,11,11,'11','2026-05-22 21:25:57.578855','2026-05-22 21:25:57.578881',58),(58,18,18,'18','2026-05-22 21:25:57.675681','2026-05-22 21:25:57.675736',59),(59,30,30,'30','2026-05-22 21:25:57.700875','2026-05-22 21:25:57.700898',60),(60,54,54,'54','2026-05-22 21:25:57.716605','2026-05-22 21:25:57.716632',61),(61,30,30,'30','2026-05-22 21:25:57.842618','2026-05-22 21:25:57.842669',62),(62,6,6,'6','2026-05-22 21:25:57.933407','2026-05-22 21:25:57.933432',63),(63,59,59,'59','2026-05-22 21:25:58.038784','2026-05-22 21:25:58.038837',64),(64,30,130,'30','2026-05-22 21:25:58.061205','2026-05-22 21:25:58.061248',65),(65,17,17,'17','2026-05-22 21:25:58.169357','2026-05-22 21:25:58.169379',66),(66,1,1,'1','2026-05-22 21:25:58.208191','2026-05-22 21:25:58.208222',67),(67,76,76,'76','2026-05-22 21:25:58.310318','2026-05-22 21:25:58.310339',68),(68,1,1,'1','2026-05-22 21:25:58.425582','2026-05-22 21:25:58.425603',69),(69,1,1,'1','2026-05-22 21:25:58.582461','2026-05-22 21:25:58.582487',70),(70,1,1,'1','2026-05-22 21:25:58.751468','2026-05-22 21:25:58.751489',71),(71,1,1,'1','2026-05-22 21:25:58.909349','2026-05-22 21:25:58.909376',72),(72,1,1,'1','2026-05-22 21:25:59.067663','2026-05-22 21:25:59.067687',73),(73,1,1,'1','2026-05-22 21:25:59.244246','2026-05-22 21:25:59.244273',74),(74,1,1,'1','2026-05-22 21:25:59.380808','2026-05-22 21:25:59.380830',75),(75,1,1,'1','2026-05-22 21:25:59.519838','2026-05-22 21:25:59.519860',76),(76,1,1,'1','2026-05-22 21:25:59.674509','2026-05-22 21:25:59.674530',77),(77,1,1,'1','2026-05-22 21:25:59.939676','2026-05-22 21:25:59.939716',78),(78,1,1,'1','2026-05-22 21:26:00.275026','2026-05-22 21:26:00.275052',79),(79,1,1,'1','2026-05-22 21:26:00.562109','2026-05-22 21:26:00.562138',80),(80,1,1,'1','2026-05-22 21:26:00.840718','2026-05-22 21:26:00.840751',81),(81,1,1,'1','2026-05-22 21:26:01.123582','2026-05-22 21:26:01.123613',82),(82,1,1,'1','2026-05-22 21:26:01.380324','2026-05-22 21:26:01.380348',83),(83,1,1,'1','2026-05-22 21:26:01.666737','2026-05-22 21:26:01.666790',84),(84,1,1,'1','2026-05-22 21:26:01.894236','2026-05-22 21:26:01.894261',85),(85,1,1,'1','2026-05-22 21:26:02.157768','2026-05-22 21:26:02.157794',86);
/*!40000 ALTER TABLE `disponibilidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_usuario_id_usu` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_usuario_id_usu` FOREIGN KEY (`user_id`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(18,'inventario','auditorialog'),(12,'inventario','auditorio'),(15,'inventario','carritoitem'),(7,'inventario','catalogo'),(13,'inventario','detallepedido'),(11,'inventario','disponibilidad'),(24,'inventario','importacioninventariolog'),(17,'inventario','notificacion'),(19,'inventario','passwordresettoken'),(14,'inventario','pedido'),(16,'inventario','pedidoevidencia'),(10,'inventario','producto'),(22,'inventario','productofoto'),(8,'inventario','rol'),(23,'inventario','subcategoria'),(20,'inventario','tipodoc'),(25,'inventario','ubicacionproducto'),(6,'inventario','usuario'),(9,'inventario','usucat'),(21,'inventario','verificacionsenatoken'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-03-16 21:34:24.094183'),(2,'contenttypes','0002_remove_content_type_name','2026-03-16 21:34:24.111478'),(3,'auth','0001_initial','2026-03-16 21:34:24.186000'),(4,'auth','0002_alter_permission_name_max_length','2026-03-16 21:34:24.203111'),(5,'auth','0003_alter_user_email_max_length','2026-03-16 21:34:24.207087'),(6,'auth','0004_alter_user_username_opts','2026-03-16 21:34:24.210954'),(7,'auth','0005_alter_user_last_login_null','2026-03-16 21:34:24.214026'),(8,'auth','0006_require_contenttypes_0002','2026-03-16 21:34:24.215677'),(9,'auth','0007_alter_validators_add_error_messages','2026-03-16 21:34:24.218861'),(10,'auth','0008_alter_user_username_max_length','2026-03-16 21:34:24.221977'),(11,'auth','0009_alter_user_last_name_max_length','2026-03-16 21:34:24.225628'),(12,'auth','0010_alter_group_name_max_length','2026-03-16 21:34:24.232202'),(13,'auth','0011_update_proxy_permissions','2026-03-16 21:34:24.235795'),(14,'auth','0012_alter_user_first_name_max_length','2026-03-16 21:34:24.238617'),(15,'inventario','0001_initial','2026-03-16 21:34:24.430660'),(16,'admin','0001_initial','2026-03-16 21:34:24.462854'),(17,'admin','0002_logentry_remove_auto_add','2026-03-16 21:34:24.470560'),(18,'admin','0003_logentry_add_action_flag_choices','2026-03-16 21:34:24.475457'),(19,'sessions','0001_initial','2026-03-16 21:34:24.485295'),(20,'inventario','0002_producto_fot_prod','2026-03-17 19:02:55.771611'),(21,'inventario','0003_usuario_fot_usu','2026-03-17 21:46:16.009522'),(22,'inventario','0004_rol_nombre_rol','2026-03-18 21:06:34.984439'),(23,'inventario','0005_pedido_detallepedido','2026-03-24 21:31:19.293409'),(24,'inventario','0006_pedido_codigo_entrega_pedido_codigo_expira_en','2026-03-26 16:04:06.431345'),(25,'inventario','0007_carritoitem','2026-03-26 16:11:13.194825'),(26,'inventario','0008_pedidaevidencia','2026-03-26 16:47:01.886641'),(27,'inventario','0009_usuario_banner_usu','2026-04-07 21:17:57.592079'),(28,'inventario','0010_prestamo_fields','2026-04-08 20:39:11.315711'),(29,'inventario','0011_notificacion','2026-04-09 17:32:56.919326'),(30,'inventario','0012_auditoria_log','2026-04-13 19:24:21.869445'),(31,'inventario','0013_usuario_perfil_extra_fields','2026-04-14 01:49:32.321234'),(32,'inventario','0014_alter_notificacion_tipo_passwordresettoken','2026-04-20 19:28:43.799227'),(33,'inventario','0015_notif_vencimiento_pedido','2026-04-20 19:28:43.820660'),(34,'inventario','0016_extensiones_plazo_pedido','2026-04-20 19:28:43.832486'),(35,'inventario','0017_tema_usuario','2026-04-20 20:24:42.121223'),(36,'inventario','0018_tipodoc_usuario_tipo_doc','2026-04-21 18:42:48.094709'),(37,'inventario','0019_usuario_verificacion_sena_documento_and_more','2026-04-21 19:50:17.613348'),(38,'inventario','0020_productofoto','2026-04-23 14:43:27.605118'),(39,'inventario','0021_alter_notificacion_tipo','2026-05-14 23:02:00.974454'),(40,'inventario','0022_producto_campos_subcategoria','2026-05-14 23:02:01.124742'),(41,'inventario','0023_importacioninventariolog','2026-05-21 22:17:21.371438'),(42,'inventario','0024_alter_subcategoria_options_and_more','2026-05-22 21:39:25.687029'),(43,'inventario','0025_pedido_motivo_rechazo','2026-05-29 21:02:59.852190'),(44,'inventario','0026_ubicacionproducto_catalogo_id_ubicacion_fk','2026-05-30 01:10:53.804287');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2f8irbzqxuzxj87i7sdxbx4shjnizq0h','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQYJF:Tb7eCihEL3hNQGfIGvifhOiLD0E5ZH9GuWZYAht2BsQ','2026-06-05 22:25:37.856053'),('6d42r7ogk83sbu30zrigw2k6zxqnvtoq','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQZA4:_R6_TmTffTyAzj1pXgpqDpt1hU9yifG87fAwNu_jaW0','2026-06-05 23:20:12.310416'),('7d0wfsjesmkfv8uq040c98a6dqjywgs8','.eJxVjDEOwjAMAP_iGUVNQojTkZ03VLbj0AJKpaadEH9HlTrAene6Nwy0reOwNV2GKUMPHk6_jEmeWneRH1Tvs5G5rsvEZk_MYZu5zVlf16P9G4zURuhBuqwFCaNDwc5Gn8h2mJP3ESm74At7lcCJL1iisJboiClYjeEcxMHnC-rlOD8:1wBM1O:fGrcb0HpCCLF1HGuq66LhTKTfmxI700Ww_pxmjGSEH8','2026-04-25 00:16:22.299983'),('7jym3jpl7b4ucxadqnqmna1pl4euryf5','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQbnX:hGncLKmUGJatBHBPai0BKF33eD_md31bM6H6xFQgqfs','2026-06-06 02:09:07.862672'),('ac60pnnnrcjf7ajpn8fl0gezuf9z0yio','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQZAX:t51Kn6BQmNBn3EYzJbkL2tig0cFncu0GuWBML4EbTjs','2026-06-05 23:20:41.577232'),('bci5ezrlsux7d6b6qofgqigoxbphduzi','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQY3O:jxWl1Forc1gSzBlXmYEeODhFZM72ymghyh-i5xTpZxI','2026-06-05 22:09:14.362657'),('eucoy7scm2cuegc1l3us5yii3t3rq6ag','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQBdb:XLsPQWbUooTgrQd1Eorbn_cvkxk3j3LitsCjX2pTQn4','2026-06-04 22:13:07.417312'),('f5gq32q5yf2oi86k91hctotaw5gh93tu','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wKjso:qNusX8sy4lYJOQnYnmgWTFdJn9Vv-NnBY44NYB1UX0U','2026-05-20 21:34:18.773946'),('g4egoc2c04u7bsb5nei6vf6anc9bj2dw','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQZSE:eq4gLMjewIUTF9A2MyFyrIueRKIbOS4SvdBCsrK-_X0','2026-06-05 23:38:58.769239'),('lz8yu41rkweeb9wu1r8tyls0j2ml74pt','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQYDX:n0tP5VkXEgCFk8y1raXYaOlpEOF76ZpL7G4bK9Iinng','2026-06-05 22:19:43.983705'),('oaf1r0aqemt8w75klveavvt9l3dmhdy7','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wVGPI:dhkq4-tilwhe6PJosIxPQK4TKrXsL4OAkpOV_KL7T2w','2026-06-18 22:19:20.812121'),('r4ggixh7674mzwa7vpenky9bhk3a1o73','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wSeDL:RG2ZcNXxJueXxwOwQ1mkwCnOtl5A8OtqeIKQAg8Vya8','2026-06-11 17:08:11.073096'),('rxpz1buh6k3pff3b9q6lebr2yj1vbfpt','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wGILm:dKjcvvBXAlFj0AAV5kMdzrJELNQWsNtYHXoN6yP5jCY','2026-05-08 15:21:50.795099'),('v4h0remtdlav6elr161ehha86cbir31x','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wLSNI:EMwcRqp_9PKcOej2saiuwhMRRc2lZkJmsKt_tFOH7bc','2026-05-22 21:04:44.594738'),('vpnu5uc1bu4m1hh6idns48i8yjmtr2or','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQYz9:zAP5_hJIoNpJuI_kf7SPgeYQeaFQrVpNeKzjp-YXb4c','2026-06-05 23:08:55.135069'),('xc1tyq6f5829rwi3twpbjhg1khoq8s1e','.eJxVjLsOwjAMAP_FM4pqSvPoyM43RHbskgJKpKadEP-OKnWA9e50b4i0rTluTZc4C4yAcPplTOmpZRfyoHKvJtWyLjObPTGHbeZWRV_Xo_0bZGoZRnDEzuG5F_TDhEiY1HW9su8mpaDibD8QqwukFkmFgkcOGkgsJsQLfL7y7TiL:1w580O:8NWikRhiJmmvACyttXYBgM5zQQW_nCHJaJ4TZcFFzJs','2026-04-07 20:05:36.745377'),('yg8qzl4ucaxwh00yznypwwwukpixcb1b','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQYnn:sLuh0lzYNYqLQFDPq7MO8pZM-8Z-cnn6XErxZbCgRrA','2026-06-05 22:57:11.435128'),('z4c7zhpaoxnu2h6w9174av2end93d0op','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQYOW:ttQJ4dUPehSqwPDi1sqWB7ti-Kh_KPuO7o6W9RLvhY8','2026-06-05 22:31:04.210544'),('z4kk264ok1sg5zvwwvf4jnb63k8rgir9','.eJxVzEEOgjAUhOG7vLUhPJGWstS1ZyBTOoRGBALFjfHuRsNCt_Nl_qc02FLfbCuXJgapReXwu3m0N44fiOODY8ISp-zLu6zZZbrPSNEPvE6Bw3l__GV6rL3UYuGt1WMRtCo7VWhLmxf0Vd4RjsGaooSndaBRMMBV6h0dgtFW9SSvN70gO2k:1wQY3f:FwRHRx6gQMAt_J66noWPzZL0mg0FQPMTHoqF5QrtAvA','2026-06-05 22:09:31.349252');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `importacion_inventario_log`
--

DROP TABLE IF EXISTS `importacion_inventario_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `importacion_inventario_log` (
  `id_log_import` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_archivo` varchar(255) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `total_productos` int(10) unsigned NOT NULL CHECK (`total_productos` >= 0),
  `total_creados` int(10) unsigned NOT NULL CHECK (`total_creados` >= 0),
  `total_actualizados` int(10) unsigned NOT NULL CHECK (`total_actualizados` >= 0),
  `total_imagenes_principales` int(10) unsigned NOT NULL CHECK (`total_imagenes_principales` >= 0),
  `total_imagenes_secundarias` int(10) unsigned NOT NULL CHECK (`total_imagenes_secundarias` >= 0),
  `total_errores` int(10) unsigned NOT NULL CHECK (`total_errores` >= 0),
  `resumen` longtext DEFAULT NULL,
  `fch_registro` datetime(6) NOT NULL,
  `id_usuario_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_log_import`),
  KEY `importacion_inventar_id_usuario_fk_50d85061_fk_usuario_i` (`id_usuario_fk`),
  CONSTRAINT `importacion_inventar_id_usuario_fk_50d85061_fk_usuario_i` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `importacion_inventario_log`
--

LOCK TABLES `importacion_inventario_log` WRITE;
/*!40000 ALTER TABLE `importacion_inventario_log` DISABLE KEYS */;
INSERT INTO `importacion_inventario_log` VALUES (1,'inventario_import_20260521_173107_ZiNhkMNxxGH-f3Uo-MU03Q.xlsx','ok',10,0,10,10,0,0,'Productos procesados: 10. Creados: 0. Actualizados: 10. Imágenes principales: 10. Imágenes secundarias: 0. Errores: 0.','2026-05-21 22:31:19.321673',1),(2,'inventario_import_20260522_162546_NNTlsPkTxx3f-pxbbHlz8w.xlsx','ok',73,73,0,73,1,0,'Productos procesados: 73. Creados: 73. Actualizados: 0. Imágenes principales: 73. Imágenes secundarias: 1. Errores: 0.','2026-05-22 21:26:02.503134',1);
/*!40000 ALTER TABLE `importacion_inventario_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificacion`
--

DROP TABLE IF EXISTS `notificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notificacion` (
  `id_noti` int(11) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(40) NOT NULL,
  `titulo` varchar(120) NOT NULL,
  `mensaje` longtext NOT NULL,
  `leida` tinyint(1) NOT NULL,
  `id_pedido_ref` int(10) unsigned DEFAULT NULL CHECK (`id_pedido_ref` >= 0),
  `fch_registro` datetime(6) NOT NULL,
  `id_usuario_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_noti`),
  KEY `notificacion_id_usuario_fk_d2a97b4e_fk_usuario_id_usu` (`id_usuario_fk`),
  CONSTRAINT `notificacion_id_usuario_fk_d2a97b4e_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificacion`
--

LOCK TABLES `notificacion` WRITE;
/*!40000 ALTER TABLE `notificacion` DISABLE KEYS */;
INSERT INTO `notificacion` VALUES (1,'pedido_creado','Pedido recibido','Tu pedido #8 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,8,'2026-04-09 17:57:26.726639',3),(2,'rechazado','Pedido cancelado por ti','Cancelaste tu pedido #8. Si fue un error, deberás crear un nuevo pedido.',1,8,'2026-04-09 18:01:47.419047',3),(3,'pedido_creado','Pedido recibido','Tu pedido #9 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,9,'2026-04-09 18:03:51.750305',3),(4,'esperando_entrega','Tu pedido está listo para entrega','Tu pedido #9 fue aprobado y está esperando ser entregado. Dirígete al almacén con tu código de entrega.',1,9,'2026-04-09 18:13:18.224608',3),(5,'entregado','Pedido entregado','Tu pedido #9 fue entregado correctamente. Recuerda devolver los materiales en la fecha acordada.',1,9,'2026-04-09 18:14:14.603897',3),(6,'staff_pedido_entregado','Pedido #9 entregado','El pedido #9 fue confirmado como entregado por juan.',1,9,'2026-04-09 18:14:14.611484',1),(7,'staff_pedido_entregado','Pedido #9 entregado','El pedido #9 fue confirmado como entregado por juan.',1,9,'2026-04-09 18:14:14.611504',2),(8,'staff_pedido_entregado','Pedido #9 entregado','El pedido #9 fue confirmado como entregado por juan.',0,9,'2026-04-09 18:14:14.611515',4),(9,'pedido_creado','Pedido recibido','Tu pedido #10 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,10,'2026-04-11 00:10:47.243357',3),(10,'staff_nuevo_pedido','Nuevo pedido #10 recibido','alex zea acaba de enviar el pedido #10 con 3 productos (3 unidades). Área: hambiente 304.',1,10,'2026-04-11 00:10:47.250195',1),(11,'staff_nuevo_pedido','Nuevo pedido #10 recibido','alex zea acaba de enviar el pedido #10 con 3 productos (3 unidades). Área: hambiente 304.',1,10,'2026-04-11 00:10:47.250224',2),(12,'staff_nuevo_pedido','Nuevo pedido #10 recibido','alex zea acaba de enviar el pedido #10 con 3 productos (3 unidades). Área: hambiente 304.',0,10,'2026-04-11 00:10:47.250237',4),(13,'esperando_entrega','Tu pedido está listo para entrega','Tu pedido #10 fue aprobado y está esperando ser entregado. Dirígete al almacén con tu código de entrega.',1,10,'2026-04-11 00:15:02.208751',3),(14,'entregado','Pedido entregado','Tu pedido #10 fue entregado correctamente. Recuerda devolver los materiales en la fecha acordada.',1,10,'2026-04-11 00:16:06.372453',3),(15,'staff_pedido_entregado','Pedido #10 entregado','El pedido #10 fue confirmado como entregado por juan.',1,10,'2026-04-11 00:16:06.376888',1),(16,'staff_pedido_entregado','Pedido #10 entregado','El pedido #10 fue confirmado como entregado por juan.',1,10,'2026-04-11 00:16:06.376950',2),(17,'staff_pedido_entregado','Pedido #10 entregado','El pedido #10 fue confirmado como entregado por juan.',0,10,'2026-04-11 00:16:06.376965',4),(18,'pedido_creado','Pedido recibido','Tu pedido #11 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,11,'2026-04-13 18:47:25.155421',3),(19,'staff_nuevo_pedido','Nuevo pedido #11 recibido','alex zea acaba de enviar el pedido #11 con 1 producto (1 unidad). Área: aula 303.',1,11,'2026-04-13 18:47:25.159320',1),(20,'staff_nuevo_pedido','Nuevo pedido #11 recibido','alex zea acaba de enviar el pedido #11 con 1 producto (1 unidad). Área: aula 303.',1,11,'2026-04-13 18:47:25.159342',2),(21,'staff_nuevo_pedido','Nuevo pedido #11 recibido','alex zea acaba de enviar el pedido #11 con 1 producto (1 unidad). Área: aula 303.',0,11,'2026-04-13 18:47:25.159351',4),(22,'esperando_entrega','Tu pedido está listo para entrega','Tu pedido #11 fue aprobado y está esperando ser entregado. Dirígete al almacén con tu código de entrega.',1,11,'2026-04-13 18:47:51.354109',3),(23,'entregado','Pedido entregado','Tu pedido #11 fue entregado correctamente. Recuerda devolver los materiales en la fecha acordada.',1,11,'2026-04-13 18:47:59.363990',3),(24,'staff_pedido_entregado','Pedido #11 entregado','El pedido #11 fue confirmado como entregado por Johan.',1,11,'2026-04-13 18:47:59.368224',1),(25,'staff_pedido_entregado','Pedido #11 entregado','El pedido #11 fue confirmado como entregado por Johan.',1,11,'2026-04-13 18:47:59.368241',2),(26,'staff_pedido_entregado','Pedido #11 entregado','El pedido #11 fue confirmado como entregado por Johan.',0,11,'2026-04-13 18:47:59.368250',4),(27,'pedido_creado','Pedido recibido','Tu pedido #12 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,12,'2026-04-13 20:34:46.736002',3),(28,'staff_nuevo_pedido','Nuevo pedido #12 recibido','alex zea acaba de enviar el pedido #12 con 4 productos (4 unidades). Área: ambiente 333.',1,12,'2026-04-13 20:34:46.739712',1),(29,'staff_nuevo_pedido','Nuevo pedido #12 recibido','alex zea acaba de enviar el pedido #12 con 4 productos (4 unidades). Área: ambiente 333.',1,12,'2026-04-13 20:34:46.739746',2),(30,'staff_nuevo_pedido','Nuevo pedido #12 recibido','alex zea acaba de enviar el pedido #12 con 4 productos (4 unidades). Área: ambiente 333.',0,12,'2026-04-13 20:34:46.739761',4),(31,'pedido_creado','Pedido recibido','Tu pedido #13 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,13,'2026-04-13 20:47:55.294217',3),(32,'staff_nuevo_pedido','Nuevo pedido #13 recibido','alex zea acaba de enviar el pedido #13 con 2 productos (2 unidades). Área: 333.',1,13,'2026-04-13 20:47:55.296670',1),(33,'staff_nuevo_pedido','Nuevo pedido #13 recibido','alex zea acaba de enviar el pedido #13 con 2 productos (2 unidades). Área: 333.',1,13,'2026-04-13 20:47:55.296687',2),(34,'staff_nuevo_pedido','Nuevo pedido #13 recibido','alex zea acaba de enviar el pedido #13 con 2 productos (2 unidades). Área: 333.',0,13,'2026-04-13 20:47:55.296696',4),(35,'pedido_creado','Pedido recibido','Tu pedido #14 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,14,'2026-04-13 20:48:11.571619',3),(36,'staff_nuevo_pedido','Nuevo pedido #14 recibido','alex zea acaba de enviar el pedido #14 con 2 productos (2 unidades). Área: 333.',1,14,'2026-04-13 20:48:11.575212',1),(37,'staff_nuevo_pedido','Nuevo pedido #14 recibido','alex zea acaba de enviar el pedido #14 con 2 productos (2 unidades). Área: 333.',1,14,'2026-04-13 20:48:11.575229',2),(38,'staff_nuevo_pedido','Nuevo pedido #14 recibido','alex zea acaba de enviar el pedido #14 con 2 productos (2 unidades). Área: 333.',0,14,'2026-04-13 20:48:11.575240',4),(39,'rechazado','Pedido rechazado','Tu pedido #12 fue rechazado por el almacenista. Si tienes dudas, comunícate con el área de almacén.',1,12,'2026-04-13 21:03:07.610767',3),(40,'rechazado','Pedido rechazado','Tu pedido #13 fue rechazado por el almacenista. Si tienes dudas, comunícate con el área de almacén.',1,13,'2026-04-13 21:21:34.608737',3),(41,'rechazado','Pedido cancelado automáticamente','Tu pedido #14 fue cancelado automáticamente porque la hora/fecha límite de entrega se venció antes de ser aprobado por almacén.',1,14,'2026-04-13 21:30:37.655833',3),(42,'solicitud_validacion_sena','Solicitud de validación SENA enviada','Tu solicitud fue enviada al administrador. Cuando apruebe la revisión, te llegará un correo con el enlace para cargar tu carnet o certificado.',0,NULL,'2026-04-23 16:28:38.354887',5),(43,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',1,NULL,'2026-04-23 16:28:38.360787',1),(44,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',0,NULL,'2026-04-23 16:28:38.360809',2),(45,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',0,NULL,'2026-04-23 16:28:38.360819',4),(46,'enlace_validacion_sena','Enlace de validación SENA enviado','Revisa tu correo. Te enviamos un enlace único para cargar la foto del carnet o un certificado vigente del SENA.',0,NULL,'2026-04-23 16:29:00.353986',5),(47,'solicitud_validacion_sena','Solicitud de validación SENA enviada','Tu solicitud fue enviada al administrador. Cuando apruebe la revisión, te llegará un correo con el enlace para cargar tu carnet o certificado.',1,NULL,'2026-05-06 18:17:11.738449',3),(48,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',1,NULL,'2026-05-06 18:17:11.740424',1),(49,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',0,NULL,'2026-05-06 18:17:11.740441',2),(50,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',0,NULL,'2026-05-06 18:17:11.740451',4),(51,'enlace_validacion_sena','Enlace de validación SENA enviado','Revisa tu correo. Te enviamos un enlace único para cargar la foto del carnet o un certificado vigente del SENA.',1,NULL,'2026-05-06 18:20:04.785742',3),(52,'solicitud_validacion_sena','Solicitud de validación SENA enviada','Tu solicitud fue enviada al administrador. Cuando apruebe la revisión, te llegará un correo con el enlace para cargar tu carnet o certificado.',0,NULL,'2026-05-06 18:31:46.267059',5),(53,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',1,NULL,'2026-05-06 18:31:46.275719',1),(54,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',0,NULL,'2026-05-06 18:31:46.275747',2),(55,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','Johan steven zea martinez solicitó validación manual de carnet SENA. Documento registrado: 1028884207.',0,NULL,'2026-05-06 18:31:46.275757',4),(56,'solicitud_validacion_sena','Solicitud de validación SENA enviada','Tu solicitud fue enviada al administrador. Cuando apruebe la revisión, te llegará un correo con el enlace para cargar tu carnet o certificado.',1,NULL,'2026-05-28 13:37:49.656637',3),(57,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',0,NULL,'2026-05-28 13:37:49.661486',1),(58,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',0,NULL,'2026-05-28 13:37:49.661506',2),(59,'staff_solicitud_validacion_sena','Solicitud manual de validación SENA','alex zea solicitó validación manual de carnet SENA. Documento registrado: 132165465.',0,NULL,'2026-05-28 13:37:49.661516',4),(60,'documento_validacion_sena','Documento recibido para validación SENA','Tu documento fue cargado correctamente. El administrador revisará la evidencia y aprobará tu cuenta si coincide.',1,NULL,'2026-05-28 13:38:34.596559',3),(61,'staff_documento_validacion_sena','Documento recibido para validación SENA','Se recibió un documento manual de alex para validación de identidad SENA.',0,NULL,'2026-05-28 13:38:34.601485',1),(62,'staff_documento_validacion_sena','Documento recibido para validación SENA','Se recibió un documento manual de alex para validación de identidad SENA.',0,NULL,'2026-05-28 13:38:34.601554',2),(63,'staff_documento_validacion_sena','Documento recibido para validación SENA','Se recibió un documento manual de alex para validación de identidad SENA.',0,NULL,'2026-05-28 13:38:34.601593',4),(64,'verificacion_sena_aprobada','Validación SENA aprobada','El administrador aprobó tu verificación manual. Ya puedes realizar pedidos normalmente.',1,NULL,'2026-05-28 13:38:44.370071',3),(65,'pedido_creado','Pedido recibido','Tu pedido #15 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',1,15,'2026-05-29 20:42:03.717569',3),(66,'staff_nuevo_pedido','Nuevo pedido #15 recibido','alex zea acaba de enviar el pedido #15 con 2 productos (2 unidades). Área: 123.',0,15,'2026-05-29 20:42:03.720925',1),(67,'staff_nuevo_pedido','Nuevo pedido #15 recibido','alex zea acaba de enviar el pedido #15 con 2 productos (2 unidades). Área: 123.',0,15,'2026-05-29 20:42:03.720945',2),(68,'staff_nuevo_pedido','Nuevo pedido #15 recibido','alex zea acaba de enviar el pedido #15 con 2 productos (2 unidades). Área: 123.',0,15,'2026-05-29 20:42:03.720956',4),(69,'rechazado','Pedido rechazado','Tu pedido #15 fue rechazado por el almacenista. Motivo: El pedido fue rechazado por no disponibilidad.',1,15,'2026-05-29 22:09:28.541451',3),(70,'pedido_creado','Pedido recibido','Tu pedido #16 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',0,16,'2026-05-29 22:12:46.979679',3),(71,'staff_nuevo_pedido','Nuevo pedido #16 recibido','alex zea acaba de enviar el pedido #16 con 2 productos (7 unidades). Área: 401.',0,16,'2026-05-29 22:12:46.989604',1),(72,'staff_nuevo_pedido','Nuevo pedido #16 recibido','alex zea acaba de enviar el pedido #16 con 2 productos (7 unidades). Área: 401.',0,16,'2026-05-29 22:12:46.989632',2),(73,'staff_nuevo_pedido','Nuevo pedido #16 recibido','alex zea acaba de enviar el pedido #16 con 2 productos (7 unidades). Área: 401.',0,16,'2026-05-29 22:12:46.989644',4),(74,'esperando_entrega','Tu pedido está listo para entrega','Tu pedido #16 fue aprobado y está esperando ser entregado. Dirígete al almacén con tu código de entrega.',0,16,'2026-05-29 22:13:36.221130',3),(75,'no_disponible','Algunos productos no están disponibles','En tu pedido #16, 1 producto no está disponible. El resto del pedido continúa en proceso. Motivo informado: maltratados',0,16,'2026-05-29 22:13:36.224335',3),(76,'entregado','Pedido entregado','Tu pedido #16 fue entregado y corresponde a material de consumo, no requiere devolución.',0,16,'2026-05-30 00:21:03.316230',3),(77,'staff_pedido_entregado','Pedido #16 entregado','El pedido #16 fue confirmado como entregado por Johan.',0,16,'2026-05-30 00:21:03.321063',1),(78,'staff_pedido_entregado','Pedido #16 entregado','El pedido #16 fue confirmado como entregado por Johan.',0,16,'2026-05-30 00:21:03.321089',2),(79,'staff_pedido_entregado','Pedido #16 entregado','El pedido #16 fue confirmado como entregado por Johan.',0,16,'2026-05-30 00:21:03.321101',4),(80,'pedido_creado','Pedido recibido','Tu pedido #17 fue enviado correctamente y está siendo revisado por el almacenista. Te notificaremos cuando cambie de estado.',0,17,'2026-05-30 00:21:46.183084',3),(81,'staff_nuevo_pedido','Nuevo pedido #17 recibido','alex zea acaba de enviar el pedido #17 con 1 producto (1 unidad). Área: 123.',0,17,'2026-05-30 00:21:46.188008',1),(82,'staff_nuevo_pedido','Nuevo pedido #17 recibido','alex zea acaba de enviar el pedido #17 con 1 producto (1 unidad). Área: 123.',0,17,'2026-05-30 00:21:46.188048',2),(83,'staff_nuevo_pedido','Nuevo pedido #17 recibido','alex zea acaba de enviar el pedido #17 con 1 producto (1 unidad). Área: 123.',0,17,'2026-05-30 00:21:46.188060',4),(84,'esperando_entrega','Tu pedido está listo para entrega','Tu pedido #17 fue aprobado y está esperando ser entregado. Dirígete al almacén con tu código de entrega.',0,17,'2026-05-30 01:19:24.725134',3);
/*!40000 ALTER TABLE `notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_reset_token`
--

DROP TABLE IF EXISTS `password_reset_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `password_reset_token` (
  `id_reset` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(128) NOT NULL,
  `creado_en` datetime(6) NOT NULL,
  `expira_en` datetime(6) NOT NULL,
  `usado_en` datetime(6) DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  PRIMARY KEY (`id_reset`),
  UNIQUE KEY `token` (`token`),
  KEY `password_reset_token_usuario_id_a175eb40_fk_usuario_id_usu` (`usuario_id`),
  CONSTRAINT `password_reset_token_usuario_id_a175eb40_fk_usuario_id_usu` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_reset_token`
--

LOCK TABLES `password_reset_token` WRITE;
/*!40000 ALTER TABLE `password_reset_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_reset_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido`
--

DROP TABLE IF EXISTS `pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pedido` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `estado` varchar(50) NOT NULL,
  `total_productos` int(10) unsigned NOT NULL CHECK (`total_productos` >= 0),
  `total_unidades` int(10) unsigned NOT NULL CHECK (`total_unidades` >= 0),
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_usuario_fk` int(11) NOT NULL,
  `codigo_entrega` varchar(6) DEFAULT NULL,
  `codigo_expira_en` datetime(6) DEFAULT NULL,
  `area_ubicacion` longtext DEFAULT NULL,
  `foto_carnet` varchar(100) DEFAULT NULL,
  `tipo_devolucion` varchar(10) DEFAULT NULL,
  `fecha_devolucion` datetime(6) DEFAULT NULL,
  `notif_vencimiento_enviada` tinyint(1) NOT NULL,
  `extensiones_plazo` smallint(5) unsigned NOT NULL CHECK (`extensiones_plazo` >= 0),
  `motivo_rechazo` longtext DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `pedido_id_usuario_fk_8b110eab_fk_usuario_id_usu` (`id_usuario_fk`),
  CONSTRAINT `pedido_id_usuario_fk_8b110eab_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido`
--

LOCK TABLES `pedido` WRITE;
/*!40000 ALTER TABLE `pedido` DISABLE KEYS */;
INSERT INTO `pedido` VALUES (1,'devuelto',1,1,'2026-03-24 21:31:39.328583','2026-04-13 18:43:55.206868',3,NULL,NULL,NULL,NULL,'global',NULL,0,0,NULL),(2,'devuelto',5,33,'2026-03-26 16:12:00.291013','2026-04-13 18:43:53.897029',3,NULL,NULL,NULL,NULL,'global',NULL,0,0,NULL),(3,'devuelto',3,26,'2026-03-26 16:48:51.329570','2026-04-13 18:43:52.282793',3,NULL,NULL,NULL,NULL,'global',NULL,0,0,NULL),(4,'devuelto',3,3,'2026-03-26 17:18:00.347171','2026-04-13 18:43:50.479433',3,NULL,NULL,NULL,NULL,'global',NULL,0,0,NULL),(5,'devuelto',2,2,'2026-03-31 16:10:59.624937','2026-04-13 18:43:44.596923',3,NULL,NULL,NULL,NULL,'global',NULL,0,0,NULL),(6,'devuelto',2,2,'2026-04-08 20:55:43.582823','2026-04-13 18:40:47.748480',3,NULL,NULL,'ambiente 304','pedidos/carnets/imagen_2026-04-08_155523483.png','global','2026-04-08 21:55:00.000000',0,0,NULL),(7,'rechazado',2,2,'2026-04-08 21:37:50.790430','2026-04-09 17:10:44.864192',3,NULL,NULL,'ambiente 215','pedidos/carnets/imagen_2026-04-08_163739379.png','global','2026-04-08 22:37:00.000000',0,0,NULL),(8,'cancelado',2,2,'2026-04-09 17:57:26.699845','2026-04-09 18:01:47.411955',3,NULL,NULL,'ambiente 204','pedidos/carnets/imagen_2026-04-09_125700567.png','mismo_dia','2026-04-09 13:10:00.000000',0,0,NULL),(9,'devuelto',1,1,'2026-04-09 18:03:51.731381','2026-04-13 18:41:20.147854',3,NULL,NULL,'ambiente 204','pedidos/carnets/imagen_2026-04-09_130340246.png','mismo_dia','2026-04-09 13:10:00.000000',0,0,NULL),(10,'devuelto',3,3,'2026-04-11 00:10:47.225213','2026-04-13 18:41:29.413028',3,NULL,NULL,'hambiente 304','pedidos/carnets/imagen_2026-04-10_191034221.png','mismo_dia','2026-04-11 22:00:00.000000',0,0,NULL),(11,'devuelto',1,1,'2026-04-13 18:47:25.142309','2026-04-13 18:56:09.529573',3,NULL,NULL,'aula 303','pedidos/carnets/imagen_2026-04-13_134712675.png','mismo_dia','2026-04-13 14:00:00.000000',0,0,NULL),(12,'rechazado',4,4,'2026-04-13 20:34:46.719464','2026-04-13 21:03:07.602617',3,NULL,NULL,'ambiente 333','pedidos/carnets/imagen_2026-04-13_153432849.png','mismo_dia','2026-04-13 20:40:00.000000',0,0,NULL),(13,'rechazado',2,2,'2026-04-13 20:47:55.282671','2026-04-13 21:21:34.600451',3,NULL,NULL,'333','pedidos/carnets/imagen_2026-04-13_154748677.png','mismo_dia','2026-04-13 21:00:00.000000',0,0,NULL),(14,'cancelado',2,2,'2026-04-13 20:48:11.558101','2026-04-13 21:30:37.634181',3,NULL,NULL,'333','pedidos/carnets/imagen_2026-04-13_154805062.png','mismo_dia','2026-04-13 21:05:00.000000',0,0,NULL),(15,'rechazado',2,2,'2026-05-29 20:42:03.706361','2026-05-29 22:09:28.520992',3,NULL,NULL,'123','','consumo',NULL,0,0,'El pedido fue rechazado por no disponibilidad.'),(16,'devuelto',2,7,'2026-05-29 22:12:46.962635','2026-05-30 00:21:03.302871',3,NULL,NULL,'401','','consumo',NULL,0,0,NULL),(17,'esperando entrega',1,1,'2026-05-30 00:21:46.164960','2026-05-30 01:19:24.702198',3,'978304','2026-05-30 03:19:24.702198','123','','consumo',NULL,0,0,NULL);
/*!40000 ALTER TABLE `pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_evidencia`
--

DROP TABLE IF EXISTS `pedido_evidencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pedido_evidencia` (
  `id_evidencia` int(11) NOT NULL AUTO_INCREMENT,
  `foto_evidencia` varchar(100) NOT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `id_pedido_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_evidencia`),
  KEY `pedido_evidencia_id_pedido_fk_132b1bf6_fk_pedido_id_pedido` (`id_pedido_fk`),
  CONSTRAINT `pedido_evidencia_id_pedido_fk_132b1bf6_fk_pedido_id_pedido` FOREIGN KEY (`id_pedido_fk`) REFERENCES `pedido` (`id_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_evidencia`
--

LOCK TABLES `pedido_evidencia` WRITE;
/*!40000 ALTER TABLE `pedido_evidencia` DISABLE KEYS */;
INSERT INTO `pedido_evidencia` VALUES (1,'pedidos/evidencias/imagen_2026-03-26_114930162.png','2026-03-26 16:49:38.238271',3),(2,'pedidos/evidencias/IMG_20260318_194002.jpg','2026-03-26 17:18:58.779816',4),(3,'pedidos/evidencias/IMG_20260318_194416.jpg','2026-03-31 16:12:44.532637',5);
/*!40000 ALTER TABLE `pedido_evidencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto` (
  `id_prod` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(255) DEFAULT NULL,
  `descripcion` longtext DEFAULT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_cat_fk` int(11) NOT NULL,
  `fot_prod` varchar(100) DEFAULT NULL,
  `cuentadante` varchar(255) DEFAULT NULL,
  `numero_placa` varchar(80) DEFAULT NULL,
  `tipo_bien` varchar(20) NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  PRIMARY KEY (`id_prod`),
  KEY `producto_id_cat_fk_3faea0b4_fk_catalogo_id_cat` (`id_cat_fk`),
  CONSTRAINT `producto_id_cat_fk_3faea0b4_fk_catalogo_id_cat` FOREIGN KEY (`id_cat_fk`) REFERENCES `catalogo` (`id_cat`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (2,'pala de construccion','La Pala Cajuelera Redonda, Puño \'d\' Truper 17193, es una herramienta esencial para cualquier trabajo de jardinería o construcción. Con un mango de madera de 50.8 cm, proporciona un agarre cómodo y seguro, permitiendo un manejo eficiente y sin esfuerzo. Su diseño robusto y duradero garantiza una larga vida útil, incluso en las condiciones más exigentes.\n\n\n\nEste modelo TR-BY de Truper, con un peso de 880 g, es ligero y fácil de manejar, lo que reduce la fatiga durante el uso prolongado. Su altura de 37.4 cm y ancho de 15.2 cm, hacen que sea compacta y fácil de almacenar cuando no se está utilizando.\n\n\n\nEl largo total de la pala es de 68.5 cm, lo que permite un alcance adecuado para la mayoría de las tareas de jardinería. La forma redonda de la cajuela facilita la excavación y el movimiento de la tierra, haciendo que sus tareas sean más eficientes.\n\n\n\nEn resumen, la Pala Cajuelera Redonda, Puño \'d\' Truper 17193, es una herramienta versátil y confiable que no puede faltar en su kit de herramientas. Ya sea que esté plantando un jardín, construyendo un camino o realizando cualquier otra tarea que requiera mover tierra, esta pala será su aliada perfecta.','2026-03-17 19:44:26.412288','2026-05-21 22:31:19.213754',2,'productos/producto_import_2_24.webp','','','devolutivo','Pendiente por asignar','unidad'),(3,'TOMA CORRIENTE','Panel empotrado de montaje en Panel de alimentación de 6xOutlet, Panel resistente montado en la pared para suministros electrónicos de oficina , 2\n\nNota: Esta página de producto sólo se vende la Tamaño 2 piezas, si necesitas otros tamaños/colores, por favor consulte a Preguntas y respuestas .\n\nDescripción:\n\n\n\nCaracterísticas: panel de toma de corriente estadounidense; 15A 110-250V, tamaño 3,39 x 3,39 pulgadas.\n\nConfiable: Panel de enchufe montado en la pared hecho de material de PC retardante de llama, resistente a altas temperaturas.\n\nFácil de usar: diseño de enchufe, evita eficazmente el peligro de electricidad, fácil de instalar y cómodo de usar.\n\nApariencia simple: el reemplazo del panel de enchufe cuadrado es exquisito, perfecto para combinar con cualquier decoración del hogar.\n\nAmplia aplicación: el panel de entrada del enchufe se utiliza universalmente en muchos lugares como hoteles, restaurantes, hogares y lugares públicos.\n\n\n\nEspecificación:\n\n\n\nMaterial: ordenador\n\n\n\nCarta del tamaño:\n\n\n\n8,6 cm x 8,6 cm/3,39 pulgadas x 3,39 pulgadas\n\n\n\nEl paquete incluye:\n\n\n\n1 panel de enchufe de pared estándar de EE. UU. (paquete de 2)\n\nQ: Sobre disponilibidad?\n\nA: Los productos que demostramos están disponibles.\n\n\n\nQ: Sobre el costo de envío y tiempo de entrega?\n\nA: Todos los productos están con envíos gratis, no necesitas pagar el costo de envío ni impuesto. Se despachan desde China, demora unos 15 a 25 días en llegar y entregar.\n\n\n\nQ: Ofrece factura?\n\nA: Ofrecemos factura en digital, puedes mandarnos un mensaje después de hacer el pedido si la necesitas. Sin embargo, esta factura no funciona como factura fiscal, no tiene sello de empresa.','2026-03-17 20:43:19.852208','2026-05-21 22:31:18.583941',3,'productos/producto_import_3_19.webp','','','devolutivo','Pendiente por asignar','unidad'),(4,'MINI INTERRUPTOR INTELIGENTE TUYA SMARTLIFE SWITCH WIFI ALEX BLANCO 16V','**** Mini Interruptor Inteligente Tuya Smartlife Switch Wifi Alexa ****\n\n\n\n¡¡ APROVECHA QUE TENEMOS POCAS UNIDADES CON PRECIO DE OFERTA !!\n\n\n\n*** NO OLVIDES GUARDAR NUESTRA PUBLICACION EN FAVORITO, ESTAMOS OFRECIENDO GRANDES DESCUENTOS EN TODO MOMENTO ***\n\n\n\nNOTA: Querido cliente si tiene alguna duda o problema con nuestro producto pongase en contacto con nosotros y con gusto lo atenderemos a la prevedad posible.\n\n\n\n*** DESPACHAMOS TU PEDIDO EN MENOS DE 24H ***\n\n\n\n--- Descripción:\n\n\n\n1. Reacondicionar aparatos o equipos ordinarios no inteligentes en dispositivos inteligentes.\n\n\n\nComo reinstalar una lámpara de escritorio en una lámpara de escritorio inteligente, el teléfono móvil puede controlar el interruptor de la luz. Para convertir el foco en un foco inteligente, solo necesita conectar un módulo de interruptor inteligente al interruptor, y luego el asistente Alexa/Google puede controlar el interruptor de luz.\n\n\n\n2. Control de aplicaciones móviles.\n\n\n\nControle el encendido y apagado del dispositivo, el tiempo, la cuenta atrás y otras funciones a través del teléfono móvil. Siempre que el teléfono móvil tenga una red, el módulo de conmutación en casa se puede controlar de forma global.\n\n\n\n*** Se puede conectar con Alexa y Google assistant ***\n\n\n\n3. Control por voz.\n\n\n\nAdmite asistentes de voz como Tmall Genie, Alexa, Google Home y realiza funciones como interruptores; \"Alexa, enciende las luces de la cocina\". Puede encender las luces en una frase y disfrutar de una vida inteligente conveniente.\n\n\n\n4. Temporización.\n\n\n\nPuede controlar el interruptor, la sincronización, la cuenta atrás y otras funciones del dispositivo a través de su teléfono móvil. Se puede pedir: apague las luces de la sala de estar después de 2 horas. 18:15 Apague el horno. Encienda la caldera a las 21:00. También puede cronometrar el dispositivo cuando no esté en casa. (Aplicación: Smart Life/TUYA Smart)\n\n\n\n5. Control de grupo.\n\n\n\nLas luces se pueden agrupar para lograr un control unificado (conmutación simultánea, sincronización, etc.);\n\n\n\n6. Internet de todo.\n\n\n\nA través de la configuración, se puede vincular con otras escenas inteligentes para hacer la vida más inteligente; por ejemplo, configure la escena del hogar: Encienda automáticamente las luces de la sala de estar, la televisión y el aire acondicionado.\n\n\n\n7. Compartir y seguridad.\n\n\n\nLa cuenta principal se puede compartir con otros miembros de la familia, y las funciones y configuraciones se conservan y copian completamente; seguridad: una vez que la cuenta principal agrega una luz, la luz se ocultará y otros usuarios ya no podrán encontrarla y agregarla; debe compartirse activamente antes de que otros puedan usarla.\n\n\n\n8. Conexión rápida Bluetooth.\n\n\n\nActive el Bluetooth, el teléfono encontrará rápidamente el dispositivo, acelerará la conexión y estabilizará la conexión.\n\n\n\n9. Memoria de estado.\n\n\n\nReanude la energía después del corte de energía, sin preocuparse por el cambio del estado del equipo y mantenga el Estado antes del corte de energía. Estaba en estado abierto antes de que se cortara la alimentación, y el estado abierto se restablece automáticamente cuando se vuelve a encender. (Se puede configurar para abrir, cerrar, modo de memoria de apagado)\n\n\n\n10. Tres métodos de cableado.(2 vías/1 vía/sin interruptor)\n\n\n\nSe puede conectar directamente al dispositivo sin conectar un interruptor.\n\n\n\nTambién se puede conectar detrás del interruptor para admitir un interruptor de control único y un interruptor de control dual. Se puede instalar directamente en la caja del interruptor para ocultar el módulo del interruptor. También se puede instalar en el interruptor de control dual sin afectar el uso del interruptor de control dual.\n\n\n\n11. Conexión WiFi, no requiere puerta de enlace.\n\n\n\nDIY, el método de conexión es simple, todos pueden DIY el dispositivo y convertir el dispositivo no inteligente en un dispositivo inteligente.\n\n\n\n--- Especificaciones:\n\n\n\nColor: blanco\n\nSalida: CA 100-240V 50/60Hz\n\nEntrada: CA 100-240V 50/60Hz\n\nWi-Fi:IEEE 802.11b/G/N\n\nMaterial: PCV-0\n\nProducto certificado: CE ROHS\n\nCorriente máxima: 16A\n\n\n\nQue incluye ?\n\n\n\n1 x Mini Interruptor Tuya Smartlife Switch Inteligente\n\n1 x Manual\n\n\n\n¡¡ APROVECHA QUE TENEMOS POCAS UNIDADES CON PRECIO DE OFERTA !!\n\n\n\n*** NO OLVIDES GUARDAR NUESTRA PUBLICACION EN FAVORITO, ESTAMOS OFRECIENDO GRANDES DESCUENTOS EN TODO MOMENTO ***\n\n\n\nNOTA: Querido cliente si tiene alguna duda o problema con nuestro producto pongase en contacto con nosotros y con gusto lo atenderemos a la prevedad posible.\n\n\n\n*** DESPACHAMOS TU PEDIDO EN MENOS DE 24H ***','2026-03-17 21:05:13.482117','2026-05-21 22:31:18.492796',3,'productos/producto_import_4_18.webp','','','devolutivo','Pendiente por asignar','unidad'),(5,'TAPABOCAS','Lote X 15 Unds De Mascarilla Tapaboca Nitta N95 Ref. 9510-1','2026-03-18 01:46:57.321225','2026-05-28 16:15:21.599297',4,'productos/producto_import_5_12.webp','','','consumo','Pendiente por asignar','unidad'),(7,'DELIXI','Llave de Tubo Ajustable y Resistente del CABLE DE LA LUCES, 20.32cm 25.4cm 30.48cm 35.56cm Herramienta Multifuncional para Instalación y Reparación de Fregaderos, Grifos y Tuberías de Agua, Construcción Metálica Duradera con Mangos Ergonómicos','2026-03-19 19:28:59.616511','2026-05-21 22:31:19.120552',2,'productos/producto_import_7_23.webp','','','devolutivo','Pendiente por asignar','unidad'),(8,'CORTADOR DE TUBOS DE PVC','Cortador de Tubos de PVC de Acero de Alta Velocidad OuDiSi - Corte Rápido, Hoja No Plegable para Tubos de Agua y Aluminio','2026-03-19 19:34:46.943231','2026-05-21 22:31:19.005189',2,'productos/producto_import_8_22.webp','','','devolutivo','Pendiente por asignar','unidad'),(9,'12 UND DESTORNILLADOR','Un juego de 12 destornilladores magnéticos, que incluye 5 destornilladores Phillips y 5 destornilladores de cabeza plana con mangos acolchados profesionales, más dos destornilladores de llave','2026-03-19 19:36:23.599281','2026-05-21 22:31:18.711998',2,'productos/producto_import_9_21.webp','','','devolutivo','Pendiente por asignar','unidad'),(11,'EJEMPLO','el ejemplo del catalogo','2026-03-31 16:07:43.362298','2026-05-21 22:31:17.933438',6,'productos/producto_import_11_15.webp','','','devolutivo','Pendiente por asignar','unidad'),(12,'COSO','un coso','2026-04-13 20:10:39.340193','2026-05-21 22:31:17.891007',6,'productos/producto_import_12_14.webp','','','devolutivo','Pendiente por asignar','unidad'),(13,'CABLE','cable luz','2026-05-14 23:04:23.262174','2026-05-21 22:31:18.468030',3,'productos/producto_import_13_17.webp','','','consumo','electricidad','rollo'),(14,'Escuadra Metálica','Carpintero 12 Pulg O 30cm','2026-05-22 21:25:53.844055','2026-05-22 21:25:53.844167',7,'productos/producto_import_14_12.webp','','','devolutivo','Pendiente por asignar','unidad'),(15,'FLEXOMETROS','de 5 metros','2026-05-22 21:25:54.105179','2026-05-22 21:25:54.105274',7,'productos/producto_import_15_13.webp','','','devolutivo','Pendiente por asignar','unidad'),(16,'LIMA CUADRADA','','2026-05-22 21:25:54.155971','2026-05-22 21:25:54.156156',7,'productos/producto_import_16_14.webp','','','devolutivo','Pendiente por asignar','unidad'),(17,'LIMA PLANA','','2026-05-22 21:25:54.196483','2026-05-22 21:25:54.196615',7,'productos/producto_import_17_15.webp','','','devolutivo','Pendiente por asignar','unidad'),(18,'LIMA REDONDA','','2026-05-22 21:25:54.229037','2026-05-22 21:25:54.229124',7,'productos/producto_import_18_16.webp','','','devolutivo','Pendiente por asignar','unidad'),(19,'LIMA SEMI CURVA PEQUEÑA','','2026-05-22 21:25:54.303617','2026-05-22 21:25:54.303689',7,'productos/producto_import_19_17.webp','','','devolutivo','Pendiente por asignar','unidad'),(20,'LIMA SEMICIRCULAR','','2026-05-22 21:25:54.329849','2026-05-22 21:25:54.329912',7,'productos/producto_import_20_18.webp','','','devolutivo','Pendiente por asignar','unidad'),(21,'LIMA TRIANGULAR','','2026-05-22 21:25:54.421057','2026-05-22 21:25:54.421182',7,'productos/producto_import_21_19.webp','','','devolutivo','Pendiente por asignar','unidad'),(22,'SEGUETAS','','2026-05-22 21:25:54.482836','2026-05-22 21:25:54.482900',7,'productos/producto_import_22_20.webp','','','devolutivo','Pendiente por asignar','unidad'),(23,'GUANTES CARNAZA AZUL','','2026-05-22 21:25:54.551029','2026-05-22 21:25:54.551096',8,'productos/producto_import_23_22.webp','','','devolutivo','Pendiente por asignar','unidad'),(24,'GUANTES DE CARNAZA AMARILLO LARGO','','2026-05-22 21:25:54.568465','2026-05-22 21:25:54.568534',8,'productos/producto_import_24_23.webp','','','devolutivo','Pendiente por asignar','unidad'),(25,'GUANTES DE CARNAZA AMARILO PEQUEÑO','','2026-05-22 21:25:54.590069','2026-05-22 21:25:54.590173',8,'productos/producto_import_25_24.webp','','','devolutivo','Pendiente por asignar','unidad'),(26,'GUANTES DE CARNAZA IMPERMEABLE','','2026-05-22 21:25:54.715109','2026-05-22 21:25:54.715177',8,'productos/producto_import_26_25.webp','','','devolutivo','Pendiente por asignar','unidad'),(27,'GUANTES DE CARNZA','','2026-05-22 21:25:54.729333','2026-05-22 21:25:54.729406',8,'productos/producto_import_27_26.webp','','','devolutivo','Pendiente por asignar','unidad'),(28,'GUANTES DE TRABAJO TELA CON PUNTOS ANTIDESLIZANTES','','2026-05-22 21:25:54.741973','2026-05-22 21:25:54.742032',8,'productos/producto_import_28_27.webp','','','devolutivo','Pendiente por asignar','unidad'),(29,'GUANTES MULTIFLEX','','2026-05-22 21:25:54.826220','2026-05-22 21:25:54.826294',8,'productos/producto_import_29_28.webp','','','devolutivo','Pendiente por asignar','unidad'),(30,'GUANTES QUIRURGICOS','guantes quirúrgicos que necesitas','2026-05-22 21:25:55.145518','2026-05-28 16:12:41.114841',8,'productos/producto_import_30_29.webp','','','consumo','Pendiente por asignar','unidad'),(31,'GUANTES VAQUETA','','2026-05-22 21:25:55.180047','2026-05-22 21:25:55.180171',8,'productos/producto_import_31_30.webp','','','devolutivo','Pendiente por asignar','unidad'),(32,'MANGA DE CARNAZA','','2026-05-22 21:25:55.493689','2026-05-22 21:25:55.493821',8,'productos/producto_import_32_31.webp','','','devolutivo','Pendiente por asignar','unidad'),(33,'PETO DE MANGA','','2026-05-22 21:25:55.552761','2026-05-22 21:25:55.552893',8,'productos/producto_import_33_32.webp','','','devolutivo','Pendiente por asignar','unidad'),(34,'PETO SIN MANGA','','2026-05-22 21:25:55.742854','2026-05-22 21:25:55.742914',8,'productos/producto_import_34_33.webp','','','devolutivo','Pendiente por asignar','unidad'),(35,'POLAINAS','','2026-05-22 21:25:55.768178','2026-05-22 21:25:55.768243',8,'productos/producto_import_35_34.webp','','','devolutivo','Pendiente por asignar','unidad'),(36,'PROTECTOR AUDITIVO TIPO TAPÓN','en caja individual','2026-05-22 21:25:55.847819','2026-05-22 21:25:55.847877',8,'productos/producto_import_36_35.webp','','','devolutivo','Pendiente por asignar','unidad'),(37,'PROTECTOR SOLAR','','2026-05-22 21:25:55.891131','2026-05-28 16:12:55.071225',8,'productos/producto_import_37_36.webp','','','consumo','Pendiente por asignar','unidad'),(38,'PROTECTORES AUDITIVOS','','2026-05-22 21:25:56.047173','2026-05-22 21:25:56.047229',8,'productos/producto_import_38_37.webp','','','devolutivo','Pendiente por asignar','unidad'),(39,'TAPABOCAS','','2026-05-22 21:25:56.115191','2026-05-28 16:15:02.922551',8,'productos/producto_import_39_38.webp','','','consumo','Pendiente por asignar','unidad'),(40,'Alicate Aislado 1000v Corte Diagonal 6\"','Características\nPara uso en lineas de media tensión hasta 1000V AC - 1500V DC\nFabricado en acero cromo vanadium, tratado termicamente para mayor durabilidad\nAcabado Niquelado resistente al oxido y corrosión\nCertificado bajo la Norma Alemana VDE, acorde a la norma IEC/EN 60900-2012\nPermite trabajar en líneas vivas, soporta medias tensiones\nTopes de seguridad, que evitan resbalamientos y contacto con la parte no aislada\nAsegurarse que las herramientas aisladas esten en un lugar seguro, seco y limpio\nRevisar su optimo estado antes de cada uso\nCapacidad de corte en cables de dureza media Ø2mm','2026-05-22 21:25:56.151346','2026-05-22 21:25:56.151398',3,'productos/producto_import_40_40.webp','','','devolutivo','Pendiente por asignar','unidad'),(41,'Alicate Aislado 1000v Universal 8\"','alicates sata\nserial=70232 PH\n* Alicate Electricista Sata Verde 8” 1000V ST72504L – Alicate universal aislado, ideal para trabajos eléctricos y mecánicos.\n* Pinza Electricista -Sata- 8” St70132St1000V – Versión de alicate para electricista con aislamiento 1000 V.\n* Alicate Aislado 1000V C/Diagonal 7” Pulgadas – Alicate de corte diagonal aislado, útil para cortar cables y alambres.\n* Juego de alicates en bandeja sata 09912 – Juego de varios alicates para taller o kit inicial.\n* SATA Alicates universales 9912 – Juego de alicates universales de mayor calidad general.','2026-05-22 21:25:56.205428','2026-05-22 21:25:56.205522',3,'productos/producto_import_41_41.webp','','','devolutivo','Pendiente por asignar','unidad'),(42,'Alicate Aislado de Punta Curva 8P 200mm 6902200 Force','Características generales de los alicates curvos Force\n\n* Forma de boca curva: permite acceder a zonas estrechas y manejar piezas en ángulo sin forzar la muñeca.  \n* Materiales resistentes: por lo general se fabrican en acero de alta resistencia para soportar torsión, presión y uso frecuente.  \n* Aplicaciones: ideales para agarrar, girar, sujetar o desmontar piezas en espacios difíciles de alcanzar (automotriz, mecánico, montaje industrial).  \n* Diseños variados: hay versiones estándar para trabajo general y otras con aislamiento para electricidad, dependiendo del uso que necesites.','2026-05-22 21:25:56.260233','2026-05-22 21:25:56.260287',3,'productos/producto_import_42_42.webp','','','devolutivo','Pendiente por asignar','unidad'),(43,'ALICATES DE PINZA','Alicate Aislado 1000v Punta Larga 6\"\nCaracterísticas:\n* Para uso en líneas de media tensión hasta 1000V AC - 1500V DC.\n* Acabado Fosfatado Negro resistente al oxido y corrosión.\n* Certificado bajo la Norma Alemana VDE, acorde a la norma IEC/EN 60900-2012.\n* Permite trabajar en líneas vivas, soporta medias tensiones.\n* Topes de seguridad, que evitan resbalamientos y contacto con la parte no aislada.\n* Asegurarse que las herramientas aisladas estén en un lugar seguro, seco y limpio.\n* Quijada de punta larga para mayor accesibilidad a espacios estrechos.\n* Capacidad de corte en cables de dureza media Ø16mm.','2026-05-22 21:25:56.323860','2026-05-22 21:25:56.323935',3,'productos/producto_import_43_43.webp','','','devolutivo','Pendiente por asignar','unidad'),(44,'BOMBILLOS','','2026-05-22 21:25:56.374276','2026-05-22 21:25:56.374361',3,'productos/producto_import_44_44.webp','','','devolutivo','Pendiente por asignar','unidad'),(45,'BREAKER 50 AMPERIOS','','2026-05-22 21:25:56.519978','2026-05-22 21:25:56.520074',3,'productos/producto_import_45_45.webp','','','devolutivo','Pendiente por asignar','unidad'),(46,'BREAKER TERMICO','','2026-05-22 21:25:56.540541','2026-05-22 21:25:56.540609',3,'productos/producto_import_46_46.webp','','','devolutivo','Pendiente por asignar','unidad'),(47,'CABLES 12 AWG','','2026-05-22 21:25:56.648231','2026-05-22 21:25:56.648303',3,'productos/producto_import_47_47.webp','','','devolutivo','Pendiente por asignar','unidad'),(48,'CABLES 14 AWG','','2026-05-22 21:25:56.669350','2026-05-22 21:25:56.669435',3,'productos/producto_import_48_48.webp','','','devolutivo','Pendiente por asignar','unidad'),(49,'CONTACTORES 110','','2026-05-22 21:25:56.931051','2026-05-22 21:25:56.931114',3,'productos/producto_import_49_49.webp','','','devolutivo','Pendiente por asignar','unidad'),(50,'CONTACTORES 220','','2026-05-22 21:25:57.010908','2026-05-22 21:25:57.010990',3,'productos/producto_import_50_50.webp','','','devolutivo','Pendiente por asignar','unidad'),(51,'DESTORNILLADOR DE ESTRELLA PUNTA ANCHA','','2026-05-22 21:25:57.087246','2026-05-22 21:25:57.087364',3,'productos/producto_import_51_51.webp','','','devolutivo','Pendiente por asignar','unidad'),(52,'DESTORNILLADOR DE ESTRELLA PUNTA MEDIANA','','2026-05-22 21:25:57.180160','2026-05-22 21:25:57.180225',3,'productos/producto_import_52_52.webp','','','devolutivo','Pendiente por asignar','unidad'),(53,'DESTORNILLADOR DE ESTRELLA PUNTA PEQUEÑA','','2026-05-22 21:25:57.266405','2026-05-22 21:25:57.266480',3,'productos/producto_import_53_53.webp','','','devolutivo','Pendiente por asignar','unidad'),(54,'DESTORNILLADOR DE PALA PUNTA GRANDE','','2026-05-22 21:25:57.374648','2026-05-22 21:25:57.374787',3,'productos/producto_import_54_54.webp','','','devolutivo','Pendiente por asignar','unidad'),(55,'DESTORNILLADOR DE PALA PUNTA MEDIANA','','2026-05-22 21:25:57.457335','2026-05-22 21:25:57.457390',3,'productos/producto_import_55_55.webp','','','devolutivo','Pendiente por asignar','unidad'),(56,'DESTORNILLADOR DE PALA PUNTA PEQUEÑA','','2026-05-22 21:25:57.470258','2026-05-22 21:25:57.470303',3,'productos/producto_import_56_56.webp','','','devolutivo','Pendiente por asignar','unidad'),(57,'DIMMER','','2026-05-22 21:25:57.518367','2026-05-22 21:25:57.518421',3,'productos/producto_import_57_57.webp','','','devolutivo','Pendiente por asignar','unidad'),(58,'EXTENSIONES','','2026-05-22 21:25:57.577934','2026-05-22 21:25:57.577992',3,'productos/producto_import_58_58.webp','','','devolutivo','Pendiente por asignar','unidad'),(59,'INTERRUPTOR DE 4 VIAS','','2026-05-22 21:25:57.673525','2026-05-22 21:25:57.673598',3,'productos/producto_import_59_59.webp','','','devolutivo','Pendiente por asignar','unidad'),(60,'INTERRUPTOR DOBLES','','2026-05-22 21:25:57.700091','2026-05-22 21:25:57.700154',3,'productos/producto_import_60_60.webp','','','devolutivo','Pendiente por asignar','unidad'),(61,'INTERRUPTOR SENCILLO','','2026-05-22 21:25:57.715610','2026-05-22 21:25:57.715673',3,'productos/producto_import_61_61.webp','','','devolutivo','Pendiente por asignar','unidad'),(62,'interruptor triple','','2026-05-22 21:25:57.840876','2026-05-22 21:25:57.840974',3,'productos/producto_import_62_62.webp','','','devolutivo','Pendiente por asignar','unidad'),(63,'PELACABLES','','2026-05-22 21:25:57.932173','2026-05-22 21:25:57.932247',3,'productos/producto_import_63_63.webp','','','devolutivo','Pendiente por asignar','unidad'),(64,'PLAFONES','','2026-05-22 21:25:58.036385','2026-05-22 21:25:58.036512',3,'productos/producto_import_64_64.webp','','','devolutivo','Pendiente por asignar','unidad'),(65,'PULSADORES','','2026-05-22 21:25:58.059526','2026-05-22 21:25:58.059628',3,'productos/producto_import_65_65.webp','','','devolutivo','Pendiente por asignar','unidad'),(66,'SENSORES DE PARED','','2026-05-22 21:25:58.168466','2026-05-22 21:25:58.168521',3,'productos/producto_import_66_66.webp','','','devolutivo','Pendiente por asignar','unidad'),(67,'TIMBRE','','2026-05-22 21:25:58.206909','2026-05-22 21:25:58.206981',3,'productos/producto_import_67_67.webp','','','devolutivo','Pendiente por asignar','unidad'),(68,'TOMAS','','2026-05-22 21:25:58.309505','2026-05-22 21:25:58.309560',3,'productos/producto_import_68_68.webp','','','devolutivo','Pendiente por asignar','unidad'),(69,'COMPUTADOR 1','cargador: SI\nmouse: N/A','2026-05-22 21:25:58.424846','2026-05-22 21:25:58.424899',9,'productos/producto_import_69_70.webp','','','devolutivo','Pendiente por asignar','unidad'),(70,'COMPUTADOR 2','cargador: SI\nmouse: N/A','2026-05-22 21:25:58.581515','2026-05-22 21:25:58.581576',9,'productos/producto_import_70_71.webp','','','devolutivo','Pendiente por asignar','unidad'),(71,'COMPUTADOR 3','cargador: SI\nmouse: N/A','2026-05-22 21:25:58.750702','2026-05-22 21:25:58.750754',9,'productos/producto_import_71_72.webp','','','devolutivo','Pendiente por asignar','unidad'),(72,'COMPUTADOR 4','cargador: SI\nmouse: N/A','2026-05-22 21:25:58.908182','2026-05-22 21:25:58.908239',9,'productos/producto_import_72_73.webp','','','devolutivo','Pendiente por asignar','unidad'),(73,'COMPUTADOR 5','cargador: SI\nmouse: N/A','2026-05-22 21:25:59.066027','2026-05-22 21:25:59.066159',9,'productos/producto_import_73_74.webp','','','devolutivo','Pendiente por asignar','unidad'),(74,'COMPUTADOR 6','cargador: SI\nmouse: N/A','2026-05-22 21:25:59.243259','2026-05-22 21:25:59.243319',9,'productos/producto_import_74_75.webp','','','devolutivo','Pendiente por asignar','unidad'),(75,'COMPUTADOR 7','cargador: compartido 7 y 8\nmouse: N/A','2026-05-22 21:25:59.379956','2026-05-22 21:25:59.380017',9,'productos/producto_import_75_76.webp','','','devolutivo','Pendiente por asignar','unidad'),(76,'COMPUTADOR 8','cargador: compartido 7 y 8\nmouse: N/A','2026-05-22 21:25:59.519075','2026-05-22 21:25:59.519125',9,'productos/producto_import_76_77.webp','','','devolutivo','Pendiente por asignar','unidad'),(77,'COMPUADOR 6','cargador: SI \nmouse: N/A','2026-05-22 21:25:59.673698','2026-05-22 21:25:59.673756',10,'productos/producto_import_77_79.webp','','','devolutivo','Pendiente por asignar','unidad'),(78,'COMPUTADOR 1','cargador: SI\nmouse: SI','2026-05-22 21:25:59.937729','2026-05-22 21:25:59.937800',10,'productos/producto_import_78_80.webp','','','devolutivo','Pendiente por asignar','unidad'),(79,'COMPUTADOR 10','cargador: SI\nmouse: N/A','2026-05-22 21:26:00.273450','2026-05-22 21:26:00.273522',10,'productos/producto_import_79_81.webp','','','devolutivo','Pendiente por asignar','unidad'),(80,'COMPUTADOR 11','cargador: SI\nmouse: N/A','2026-05-22 21:26:00.560728','2026-05-22 21:26:00.560932',10,'productos/producto_import_80_82.webp','','','devolutivo','Pendiente por asignar','unidad'),(81,'COMPUTADOR 12','cargador: N/A\nmouse: N/A','2026-05-22 21:26:00.838740','2026-05-22 21:26:00.838828',10,'productos/producto_import_81_83.webp','','','devolutivo','Pendiente por asignar','unidad'),(82,'COMPUTADOR 4','cargador: SI\nmouse: SI','2026-05-22 21:26:01.121825','2026-05-22 21:26:01.121896',10,'productos/producto_import_82_84.webp','','','devolutivo','Pendiente por asignar','unidad'),(83,'COMPUTADOR 5','cargador: SI\nmouse: SI','2026-05-22 21:26:01.379377','2026-05-22 21:26:01.379433',10,'productos/producto_import_83_85.webp','','','devolutivo','Pendiente por asignar','unidad'),(84,'COMPUTADOR 7','cargador: SI\nmouse: SI','2026-05-22 21:26:01.665478','2026-05-22 21:26:01.665531',10,'productos/producto_import_84_86.webp','','','devolutivo','Pendiente por asignar','unidad'),(85,'COMPUTADOR 8','cargador: SI\nmouse: SI','2026-05-22 21:26:01.893168','2026-05-22 21:26:01.893227',10,'productos/producto_import_85_87.webp','','','devolutivo','Pendiente por asignar','unidad'),(86,'COMPUTADOR 9','cargador: SI\nmouse: SI','2026-05-22 21:26:02.155954','2026-05-22 21:26:02.156072',10,'productos/producto_import_86_88.webp','','','devolutivo','Pendiente por asignar','unidad');
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_foto`
--

DROP TABLE IF EXISTS `producto_foto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto_foto` (
  `id_foto` int(11) NOT NULL AUTO_INCREMENT,
  `foto` varchar(100) NOT NULL,
  `orden` smallint(5) unsigned NOT NULL CHECK (`orden` >= 0),
  `fch_registro` datetime(6) NOT NULL,
  `id_prod_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_foto`),
  KEY `producto_foto_id_prod_fk_18eca5a9_fk_producto_id_prod` (`id_prod_fk`),
  CONSTRAINT `producto_foto_id_prod_fk_18eca5a9_fk_producto_id_prod` FOREIGN KEY (`id_prod_fk`) REFERENCES `producto` (`id_prod`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_foto`
--

LOCK TABLES `producto_foto` WRITE;
/*!40000 ALTER TABLE `producto_foto` DISABLE KEYS */;
INSERT INTO `producto_foto` VALUES (1,'productos/fotos/producto_sec_import_22_2_1.webp',1,'2026-05-22 21:26:02.500994',22);
/*!40000 ALTER TABLE `producto_foto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_subcategorias`
--

DROP TABLE IF EXISTS `producto_subcategorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto_subcategorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `subcategoria_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `producto_subcategorias_producto_id_subcategoria_id_2055dee1_uniq` (`producto_id`,`subcategoria_id`),
  KEY `producto_subcategori_subcategoria_id_99e7a24a_fk_subcatego` (`subcategoria_id`),
  CONSTRAINT `producto_subcategori_subcategoria_id_99e7a24a_fk_subcatego` FOREIGN KEY (`subcategoria_id`) REFERENCES `subcategoria` (`id_subcat`),
  CONSTRAINT `producto_subcategorias_producto_id_cba77824_fk_producto_id_prod` FOREIGN KEY (`producto_id`) REFERENCES `producto` (`id_prod`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_subcategorias`
--

LOCK TABLES `producto_subcategorias` WRITE;
/*!40000 ALTER TABLE `producto_subcategorias` DISABLE KEYS */;
INSERT INTO `producto_subcategorias` VALUES (15,5,14),(1,13,1),(19,23,26),(28,24,27),(29,25,27),(30,26,27),(25,27,26),(34,28,29),(33,29,29),(31,30,28),(32,31,27);
/*!40000 ALTER TABLE `producto_subcategorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL AUTO_INCREMENT,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `nombre_rol` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,NULL,NULL,'admin'),(2,NULL,NULL,'almacenista'),(3,NULL,NULL,'usuario'),(4,NULL,NULL,'instructor'),(5,NULL,NULL,'aprendiz');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subcategoria`
--

DROP TABLE IF EXISTS `subcategoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subcategoria` (
  `id_subcat` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_subcategoria` varchar(255) NOT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_cat_fk` int(11) NOT NULL,
  `subcategoria_padre_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_subcat`),
  UNIQUE KEY `uq_subcat_catalogo_padre_nombre` (`id_cat_fk`,`subcategoria_padre_id`,`nombre_subcategoria`),
  KEY `subcategoria_id_cat_fk_601d9c88` (`id_cat_fk`),
  KEY `subcategoria_subcategoria_padre_i_5d8e65fd_fk_subcatego` (`subcategoria_padre_id`),
  CONSTRAINT `subcategoria_id_cat_fk_601d9c88_fk_catalogo_id_cat` FOREIGN KEY (`id_cat_fk`) REFERENCES `catalogo` (`id_cat`),
  CONSTRAINT `subcategoria_subcategoria_padre_i_5d8e65fd_fk_subcatego` FOREIGN KEY (`subcategoria_padre_id`) REFERENCES `subcategoria` (`id_subcat`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcategoria`
--

LOCK TABLES `subcategoria` WRITE;
/*!40000 ALTER TABLE `subcategoria` DISABLE KEYS */;
INSERT INTO `subcategoria` VALUES (1,'cables','2026-05-14 23:04:24.120034','2026-05-14 23:04:24.120036',3,NULL),(2,'prueba_guardado_ui','2026-05-22 22:09:31.343844','2026-05-22 22:09:31.343846',2,NULL),(11,'cabeza','2026-05-22 22:31:53.070283','2026-05-22 22:31:53.070288',4,NULL),(13,'arriba','2026-05-22 22:37:43.797831','2026-05-22 22:37:43.797837',4,11),(14,'boca','2026-05-22 22:37:51.572524','2026-05-22 22:37:51.572529',4,13),(26,'guantes','2026-05-22 23:41:18.424170','2026-05-22 23:41:18.424172',8,NULL),(27,'cuero','2026-05-22 23:42:12.712564','2026-05-22 23:42:12.712567',8,26),(28,'desechables','2026-05-22 23:42:21.695500','2026-05-22 23:42:21.695503',8,26),(29,'guantes de electricidad','2026-05-22 23:42:44.828012','2026-05-22 23:42:44.828015',8,26),(31,'destornillador','2026-05-23 01:13:27.742565','2026-05-23 01:13:27.742568',3,NULL),(32,'hola','2026-05-29 23:43:04.656368','2026-05-29 23:43:04.656370',4,11);
/*!40000 ALTER TABLE `subcategoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_doc`
--

DROP TABLE IF EXISTS `tipo_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipo_doc` (
  `id_tipo_doc` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  `codigo` varchar(10) NOT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_tipo_doc`),
  UNIQUE KEY `nombre` (`nombre`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_doc`
--

LOCK TABLES `tipo_doc` WRITE;
/*!40000 ALTER TABLE `tipo_doc` DISABLE KEYS */;
INSERT INTO `tipo_doc` VALUES (1,'Cedula de ciudadania','CC','2026-04-21 18:42:48.072884','2026-04-21 18:42:48.072884'),(2,'Tarjeta de identidad','TI','2026-04-21 18:42:48.072884','2026-04-21 18:42:48.072884');
/*!40000 ALTER TABLE `tipo_doc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ubicacion_producto`
--

DROP TABLE IF EXISTS `ubicacion_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ubicacion_producto` (
  `id_ubicacion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) NOT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_ubicacion`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ubicacion_producto`
--

LOCK TABLES `ubicacion_producto` WRITE;
/*!40000 ALTER TABLE `ubicacion_producto` DISABLE KEYS */;
INSERT INTO `ubicacion_producto` VALUES (1,'ELECTRICIDAD','2026-05-30 01:11:10.437573','2026-05-30 01:11:10.437576');
/*!40000 ALTER TABLE `ubicacion_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usu_cat`
--

DROP TABLE IF EXISTS `usu_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usu_cat` (
  `id_usu_cat` int(11) NOT NULL AUTO_INCREMENT,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  `id_cat_fk` int(11) NOT NULL,
  `id_usuario_fk` int(11) NOT NULL,
  PRIMARY KEY (`id_usu_cat`),
  KEY `usu_cat_id_cat_fk_644c2db6_fk_catalogo_id_cat` (`id_cat_fk`),
  KEY `usu_cat_id_usuario_fk_e97f352c_fk_usuario_id_usu` (`id_usuario_fk`),
  CONSTRAINT `usu_cat_id_cat_fk_644c2db6_fk_catalogo_id_cat` FOREIGN KEY (`id_cat_fk`) REFERENCES `catalogo` (`id_cat`),
  CONSTRAINT `usu_cat_id_usuario_fk_e97f352c_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usu_cat`
--

LOCK TABLES `usu_cat` WRITE;
/*!40000 ALTER TABLE `usu_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `usu_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuario` (
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `id_usu` int(11) NOT NULL AUTO_INCREMENT,
  `cc` varchar(20) DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `apellido` varchar(255) DEFAULT NULL,
  `correo` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `id_rol_fk` int(11) DEFAULT NULL,
  `fot_usu` varchar(100) DEFAULT NULL,
  `banner_usu` varchar(100) DEFAULT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `programa_formacion` varchar(255) DEFAULT NULL,
  `centro_desarrollo` varchar(255) DEFAULT NULL,
  `tema` varchar(10) NOT NULL,
  `id_tipo_doc_fk` int(11) DEFAULT NULL,
  `verificacion_sena_documento` varchar(100) DEFAULT NULL,
  `verificacion_sena_estado` varchar(25) NOT NULL,
  `verificacion_sena_imagen` varchar(100) DEFAULT NULL,
  `verificacion_sena_observacion` longtext DEFAULT NULL,
  `verificacion_sena_solicitada_en` datetime(6) DEFAULT NULL,
  `verificacion_sena_validada_en` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_usu`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `cc` (`cc`),
  KEY `usuario_id_rol_fk_62692023_fk_rol_id_rol` (`id_rol_fk`),
  KEY `usuario_id_tipo_doc_fk_7066318d_fk_tipo_doc_id_tipo_doc` (`id_tipo_doc_fk`),
  CONSTRAINT `usuario_id_rol_fk_62692023_fk_rol_id_rol` FOREIGN KEY (`id_rol_fk`) REFERENCES `rol` (`id_rol`),
  CONSTRAINT `usuario_id_tipo_doc_fk_7066318d_fk_tipo_doc_id_tipo_doc` FOREIGN KEY (`id_tipo_doc_fk`) REFERENCES `tipo_doc` (`id_tipo_doc`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES ('2026-05-30 00:21:54.471252',1,1,'1202220000','Johan','zea','zeamartinezjohan@gmail.com','pbkdf2_sha256$600000$X4HaAbNyDw4t3FXdsYgbmF$eoN8tVmPxIxaQmDNx1f358vk30VOP/GR8APCs2LQHm4=',1,1,1,'usuarios/imagen_2026-04-07_162157371.png','usuarios/banners/portada-color_4Ls76TD.png','+57 302 574 9922','Prog','Centro','claro',1,'','pendiente','',NULL,NULL,NULL),('2026-04-21 16:43:59.168571',0,2,'10000000000','juan','perez','juanperez@gmail.com','pbkdf2_sha256$600000$ixkTukcc9UUhnbiopezThM$I53xJ5S12eQKD2pbM2QV+a/O2+KHxpNxAW9aGS8S4Bs=',1,0,2,'',NULL,NULL,NULL,NULL,'oscuro',NULL,NULL,'pendiente',NULL,NULL,NULL,NULL),('2026-05-30 00:21:14.704747',0,3,'132165465','alex','zea','alex@gmail.com','pbkdf2_sha256$600000$ZqgvHgVRvo61jAsKH9B9Ot$QbonHh+GBdChAKpwGWIybBvXiBX1os4mWHvzaqkgoM8=',1,0,3,'usuarios/bmw-f30-widebody-f30_3840x2560_xtrafondos.com_1.jpg','usuarios/banners/portada-color_4z1l3rn.png',NULL,NULL,NULL,'claro',NULL,'usuarios/validacion_manual/Image_2026-05-26_at_11.49.03_AM.jpeg','validado',NULL,'Validación manual aprobada por administración.','2026-05-28 13:38:08.552938','2026-05-28 13:38:44.365535'),('2026-05-29 23:26:15.352637',0,4,'12123123','ejemplo','ejempl','ejemplo@gmail.com','pbkdf2_sha256$600000$2wzABmkTzEFagiD2MKATsN$f+lMYpTsqccU/sNUcAuEhTtYQz1RbzxyqXp6w0FOzQ4=',1,0,2,'usuarios/imagen_2026-04-07_172706958.png','usuarios/banners/bmw-f30-widebody-f30_3840x2560_xtrafondos.com_1.jpg',NULL,NULL,NULL,'claro',NULL,NULL,'pendiente',NULL,NULL,NULL,NULL),('2026-05-28 16:15:31.187544',0,5,'1028884207','Johan steven','zea martinez','sttn247@gmail.com','pbkdf2_sha256$600000$A2IvRoRc805EUlImEnoKQa$NogPkDJjhIf1WGzVwRLfuiiGxqdjGV3xwz2f41gGiB8=',1,0,3,'','',NULL,NULL,NULL,'claro',1,'','pendiente','','Enlace manual generado en localhost; envío por correo no disponible.',NULL,NULL),('2026-05-14 21:44:11.807022',0,8,'12312312','johan','zea','johan@gmail.com','pbkdf2_sha256$600000$Mn6lCjMaa6VsZU9XBt2nlI$Kgxm0iz7t18YXe+8LvN1LzWg4kfy22fUHNy92hAcyA8=',1,0,3,'','',NULL,NULL,NULL,'claro',1,'','pendiente','',NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_groups`
--

DROP TABLE IF EXISTS `usuario_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuario_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_groups_usuario_id_group_id_2e3cd638_uniq` (`usuario_id`,`group_id`),
  KEY `usuario_groups_group_id_c67c8651_fk_auth_group_id` (`group_id`),
  CONSTRAINT `usuario_groups_group_id_c67c8651_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `usuario_groups_usuario_id_161fc80c_fk_usuario_id_usu` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_groups`
--

LOCK TABLES `usuario_groups` WRITE;
/*!40000 ALTER TABLE `usuario_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_user_permissions`
--

DROP TABLE IF EXISTS `usuario_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuario_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_user_permissions_usuario_id_permission_id_3db58b8c_uniq` (`usuario_id`,`permission_id`),
  KEY `usuario_user_permiss_permission_id_a8893ce7_fk_auth_perm` (`permission_id`),
  CONSTRAINT `usuario_user_permiss_permission_id_a8893ce7_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `usuario_user_permissions_usuario_id_693d9c50_fk_usuario_id_usu` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_user_permissions`
--

LOCK TABLES `usuario_user_permissions` WRITE;
/*!40000 ALTER TABLE `usuario_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `verificacion_sena_token`
--

DROP TABLE IF EXISTS `verificacion_sena_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `verificacion_sena_token` (
  `id_token` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(128) NOT NULL,
  `creado_en` datetime(6) NOT NULL,
  `expira_en` datetime(6) NOT NULL,
  `usado_en` datetime(6) DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  PRIMARY KEY (`id_token`),
  UNIQUE KEY `token` (`token`),
  KEY `verificacion_sena_token_usuario_id_cc753dbb_fk_usuario_id_usu` (`usuario_id`),
  CONSTRAINT `verificacion_sena_token_usuario_id_cc753dbb_fk_usuario_id_usu` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `verificacion_sena_token`
--

LOCK TABLES `verificacion_sena_token` WRITE;
/*!40000 ALTER TABLE `verificacion_sena_token` DISABLE KEYS */;
INSERT INTO `verificacion_sena_token` VALUES (2,'jUUBJzT2VWeRRDSqQdiY9Y3livYAYwwF3coMcZE80jI','2026-04-23 16:28:59.345251','2026-04-23 20:28:59.341161','2026-05-06 18:31:57.495292',5),(3,'if7pCc1EafYSnPp26cOHjSNDaVycKmgBAv6qP2NrxMY','2026-05-06 18:20:03.279570','2026-05-06 22:20:03.273340','2026-05-28 13:38:07.523433',3),(4,'6Q-oVkzEomV97uNflJNM3_i7R7QcqTAIC0_8niF3v38','2026-05-06 18:31:57.499680','2026-05-06 22:31:57.495292','2026-05-06 18:31:58.834922',5),(5,'9RR9Rig9Q_er7KVnxz-nua9u2JsNJhPQuB8SE144K54','2026-05-06 18:36:57.498104','2026-05-06 22:36:57.496984','2026-05-06 18:36:58.532902',5),(6,'IefRJeeoHNFoiwbz4uAwKX_o5is2HyM25ma8DUJ3z6w','2026-05-06 18:40:03.057303','2026-05-06 22:40:03.055892','2026-05-06 18:40:04.218405',5),(7,'2M6ylvBWwcLErndSstE2zaXSWzeXEQlgwy9svAgRPGo','2026-05-06 19:25:17.893052','2026-05-06 23:25:17.890907',NULL,5),(8,'LzNWlvAJko0pBX7uyB09DaJQbpQpp5BrsnBxUv6yddc','2026-05-28 13:38:07.535981','2026-05-28 17:38:07.523433','2026-05-28 13:38:34.594185',3);
/*!40000 ALTER TABLE `verificacion_sena_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'invsena'
--

--
-- Dumping routines for database 'invsena'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-04 17:20:07
