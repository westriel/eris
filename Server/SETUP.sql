-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 30, 2021 at 04:47 PM
-- Server version: 10.4.18-MariaDB
-- PHP Version: 8.0.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `eris`
--

-- --------------------------------------------------------

--
-- Table structure for table `notification_settings`
--

CREATE TABLE `notification_settings` (
  `user_name` varchar(30) NOT NULL,
  `address` varchar(255) NOT NULL,
  `commit_update` tinyint(1) DEFAULT NULL,
  `update_update` tinyint(4) DEFAULT NULL,
  `auto_update` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `repo_access`
--

CREATE TABLE `repo_access` (
  `address` varchar(255) NOT NULL,
  `user_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Triggers `repo_access`
--
DELIMITER $$
CREATE TRIGGER `new_repo_access` AFTER INSERT ON `repo_access` FOR EACH ROW INSERT INTO notification_settings (user_name, address, commit_update, update_update, auto_update) VALUES (new.user_name, new.address, '1', '1', '1')
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `svn_repo`
--

CREATE TABLE `svn_repo` (
  `address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user_name` varchar(25) NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  `current_repo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `notification_settings`
--
ALTER TABLE `notification_settings`
  ADD PRIMARY KEY (`user_name`,`address`),
  ADD KEY `repo_address` (`address`);

--
-- Indexes for table `repo_access`
--
ALTER TABLE `repo_access`
  ADD PRIMARY KEY (`address`,`user_name`),
  ADD KEY `FK_USERNAME` (`user_name`);

--
-- Indexes for table `svn_repo`
--
ALTER TABLE `svn_repo`
  ADD PRIMARY KEY (`address`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_name`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `notification_settings`
--
ALTER TABLE `notification_settings`
  ADD CONSTRAINT `notification_settings_ibfk_1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`),
  ADD CONSTRAINT `notification_settings_ibfk_2` FOREIGN KEY (`address`) REFERENCES `svn_repo` (`address`);

--
-- Constraints for table `repo_access`
--
ALTER TABLE `repo_access`
  ADD CONSTRAINT `FK_ADDRESS` FOREIGN KEY (`address`) REFERENCES `svn_repo` (`address`),
  ADD CONSTRAINT `FK_USERNAME` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
