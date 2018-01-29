CREATE TABLE `promo_contents` (
  `content_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gamespace_id` int(11) NOT NULL,
  `content_name` varchar(32) NOT NULL DEFAULT '',
  `content_json` json NOT NULL,
  PRIMARY KEY (`content_id`),
  UNIQUE KEY `gamespace_id` (`gamespace_id`,`content_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
