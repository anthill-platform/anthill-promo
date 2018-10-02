CREATE TABLE `promo_code` (
  `code_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gamespace_id` int(11) NOT NULL,
  `code_key` varchar(255) NOT NULL DEFAULT '',
  `code_amount` int(11) NOT NULL DEFAULT '1',
  `code_expires` datetime NOT NULL,
  `code_contents` json NOT NULL,
  PRIMARY KEY (`code_id`),
  UNIQUE KEY `gamespace_id` (`gamespace_id`,`code_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
