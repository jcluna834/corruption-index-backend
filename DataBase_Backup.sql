#TABLA ENTITY
CREATE TABLE `entity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `responsible_code` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

#REGISTERS ENTITY
INSERT INTO plagiarism_detection.entity (id, name, description, responsible_code) VALUES(1, 'Entidad estatal Cauca', 'Entidad estatal Cauca', 1);

#-------------------------------------------------------------------
#TABLA announcement
CREATE TABLE `announcement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `startDate` datetime NOT NULL,
  `endDate` datetime NOT NULL,
  `responsible_code` int(11) DEFAULT NULL,
  `entity_code` int(11) NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `announcement_entity_fk` (`entity_code`),
  CONSTRAINT `announcement_entity_fk` FOREIGN KEY (`entity_code`) REFERENCES `entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

#REGISTERS announcement
INSERT INTO plagiarism_detection.announcement (id, name, description, startDate, endDate, responsible_code, entity_code, created_date, updated_date, is_deleted) 
VALUES(1, 'Convocatoria construcción puente', 'Convocatoria construcción puente', '2021-09-01 12:23:00.000', '2021-09-30 12:23:00.000', 1, 1, '2021-09-07 12:23:28.000', '2021-09-07 12:23:28.000', 0);

#-------------------------------------------------------------------
#TABLA analysistype
CREATE TABLE `analysistype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(75) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

#REGISTERS analysistype
INSERT INTO plagiarism_detection.analysistype (id, name, description) VALUES(1, 'Global', 'Análisis de similitud contra todos los documentos indexados');
INSERT INTO plagiarism_detection.analysistype (id, name, description) VALUES(2, 'Entidad', 'nmálisis de similitud contra los documentos pertenecientes a la entidad');
INSERT INTO plagiarism_detection.analysistype (id, name, description) VALUES(3, 'Convocatoria', 'nmálisis de similitud contra los documentos pertenecientes a la Convocatoria');
INSERT INTO plagiarism_detection.analysistype (id, name, description) VALUES(4, 'Entre Documentos', 'nmálisis de similitud entre dos documentos');


#-------------------------------------------------------------------
#TABLA documentstatus
CREATE TABLE `documentstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(75) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

#REGISTERS documentstatus
INSERT INTO plagiarism_detection.documentstatus (id, name, description) VALUES(1, 'Subido', 'Documento subido a la BD y almacenado f�sicamente');
INSERT INTO plagiarism_detection.documentstatus (id, name, description) VALUES(2, 'Analizado', 'Documento con an�lisis de similitud');
INSERT INTO plagiarism_detection.documentstatus (id, name, description) VALUES(3, 'Indexado', 'Documento indexado en Elastic Search');


#-------------------------------------------------------------------
#TABLA commonphrase
CREATE TABLE `commonphrase` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(200) NOT NULL,
  `phrase` text DEFAULT NULL,
  `announcementCode` int(11) NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `is_deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phrase` (`phrase`,`is_deleted`) USING HASH,
  KEY `announcement_entity_fk` (`announcementCode`),
  CONSTRAINT `commonPhrase_announcement_fk` FOREIGN KEY (`announcementCode`) REFERENCES `announcement` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

#REGISTERS commonphrase
INSERT INTO plagiarism_detection.commonphrase (id, description, phrase, announcementCode, created_date, updated_date, is_deleted) VALUES(1, 'Frease común de prueba', 'Esta es una prueba', 1, '2021-09-07 13:26:47.000', '2021-09-07 13:26:47.000', 0);
INSERT INTO plagiarism_detection.commonphrase (id, description, phrase, announcementCode, created_date, updated_date, is_deleted) VALUES(2, 'test', 'Esto ha motivado a que las entidades promuevan estrategias anticorrupción, la mayoría de estas estrategias son manuales y de índole social.', 1, '2021-09-09 09:17:59.000', '2021-09-09 09:17:59.000', 1);

#-------------------------------------------------------------------
#TABLA documents
CREATE TABLE `documents` (
  `id` varchar(75) NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `is_deleted` int(11) DEFAULT NULL,
  `content` text NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `fileName` varchar(200) NOT NULL,
  `responsibleCode` int(11) DEFAULT NULL,
  `announcementCode` int(11) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`,`is_deleted`),
  KEY `documents|title|is_deleted` (`title`,`is_deleted`),
  KEY `documents_announcement_fk` (`announcementCode`),
  KEY `documents_documentstatus_fk` (`status`),
  CONSTRAINT `documents_announcement_fk` FOREIGN KEY (`announcementCode`) REFERENCES `announcement` (`id`),
  CONSTRAINT `documents_documentstatus_fk` FOREIGN KEY (`status`) REFERENCES `documentstatus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

#REGISTERS 

#-------------------------------------------------------------------
#TABLA similardocument
CREATE TABLE `similardocument` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `analysisDocumentCode` varchar(75) NOT NULL,
  `similarDocumentCode` varchar(75) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `similar_analysisDocument_fk` (`analysisDocumentCode`),
  KEY `similar_similarDocument_fk` (`similarDocumentCode`),
  CONSTRAINT `similarDocumentt_fk1` FOREIGN KEY (`analysisDocumentCode`) REFERENCES `documents` (`id`),
  CONSTRAINT `similarDocumentt_fk2` FOREIGN KEY (`similarDocumentCode`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

#REGISTERS 

#-------------------------------------------------------------------
#TABLA analysishistory
CREATE TABLE `analysishistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `documentCode` varchar(75) NOT NULL,
  `similarDocumentCode` varchar(75) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  `analysisTypeCode` int(1) NOT NULL DEFAULT 0,
  `collectionCode` varchar(75) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `analysisHistory` (`documentCode`,`similarDocumentCode`),
  KEY `analysisHistory_type_fk` (`analysisTypeCode`),
  KEY `analysishistory_documents_fk2` (`similarDocumentCode`),
  CONSTRAINT `analysisHistory_type_fk` FOREIGN KEY (`analysisTypeCode`) REFERENCES `analysistype` (`id`),
  CONSTRAINT `analysishistory_documents_fk` FOREIGN KEY (`documentCode`) REFERENCES `documents` (`id`),
  CONSTRAINT `analysishistory_documents_fk2` FOREIGN KEY (`similarDocumentCode`) REFERENCES `documents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;

#REGISTERS 