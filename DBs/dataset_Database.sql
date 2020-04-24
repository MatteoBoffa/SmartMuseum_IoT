
#create empty Database: `dataset_Database`
#...

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


#create table `temperatures`

CREATE TABLE `temperatures` (
  `id` mediumint(9) NOT NULL,
  `room` int(11) NOT NULL,
  `temperature` float NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


#set 'id' as primary key

ALTER TABLE `temperatures`
  ADD PRIMARY KEY (`id`);


#create table `positions`


CREATE TABLE `positions` (
  `id` mediumint(9) NOT NULL,
  `room` int(11) NOT NULL,
  `macEstimote` varchar(20) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

#as before
ALTER TABLE `positions`
  ADD PRIMARY KEY (`id`);


