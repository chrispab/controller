-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 03, 2016 at 11:59 AM
-- Server version: 5.5.52-0+deb8u1
-- PHP Version: 5.6.24-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `sensordata_db`
--
CREATE DATABASE IF NOT EXISTS `sensordata_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `sensordata_db`;

-- --------------------------------------------------------

--
-- Table structure for table `thdata`
--

CREATE TABLE IF NOT EXISTS `thdata` (
`id` int(6) unsigned NOT NULL,
  `sample_dt` datetime DEFAULT NULL,
  `temperature` decimal(3,1) DEFAULT NULL,
  `humidity` decimal(3,1) DEFAULT NULL,
  `heaterstate` tinyint(1) DEFAULT NULL,
  `ventstate` tinyint(1) DEFAULT NULL,
  `fanstate` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `thdata`
--

INSERT INTO `thdata` (`id`, `sample_dt`, `temperature`, `humidity`, `heaterstate`, `ventstate`, `fanstate`) VALUES
(1, '2016-10-03 11:59:03', 16.3, 43.1, 0, 1, 1),
(2, '2016-10-03 11:59:09', 16.4, 43.8, 0, 1, 1),
(3, '2016-10-03 11:59:09', 16.4, 43.8, 0, 0, 1),
(4, '2016-10-03 11:59:23', 16.3, 44.2, 0, 0, 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `thdata`
--
ALTER TABLE `thdata`
 ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `thdata`
--
ALTER TABLE `thdata`
MODIFY `id` int(6) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
