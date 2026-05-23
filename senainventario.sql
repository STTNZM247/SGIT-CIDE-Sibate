
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

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `invsena` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `invsena`;
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
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalogo` (
  `id_cat` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_catalogo` varchar(255) DEFAULT NULL,
  `descripcion` longtext DEFAULT NULL,
  `fch_registro` datetime(6) DEFAULT NULL,
  `fch_ult_act` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_cat`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
  PRIMARY KEY (`id_pedido`),
  KEY `pedido_id_usuario_fk_8b110eab_fk_usuario_id_usu` (`id_usuario_fk`),
  CONSTRAINT `pedido_id_usuario_fk_8b110eab_fk_usuario_id_usu` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

