
#create empty db: `credentials_Database`
#...

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

# create table `credentialsServer`


CREATE TABLE `credentialsServer` (
  `ipServer` varchar(20) DEFAULT NULL,
  `TCPPort` int(11) DEFAULT NULL,
  `whoIAm` varchar(20) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `lastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


#create table `estimotes`


CREATE TABLE `estimotes` (
  `name` varchar(20) NOT NULL,
  `macEstimote` varchar(20) NOT NULL,
  `avaiable` tinyint(1) NOT NULL,
  `chatId` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


# insert usable estimotes inside `estimotes`


INSERT INTO `estimotes` (`name`, `macEstimote`, `avaiable`, `chatId`) VALUES
('Dalì', 'd5:e5:4c:1d:e2:1a', 1, NULL),
('Matisse', 'd3:43:07:2c:aa:64', 1, NULL),
('Picasso', 'dd:fe:f3:ab:88:9d', 1, NULL),
('Kahlo', 'f9:e3:a1:96:eb:c4', 1, NULL),
('Abramovic', 'f1:ea:97:80:77:fd', 1, NULL);
COMMIT;


