CREATE TABLE `promo_code_users` (
  `record_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gamespace_id` int(11) DEFAULT NULL,
  `code_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;