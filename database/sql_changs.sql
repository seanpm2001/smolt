--We are up to date

-- Not!

ALTER TABLE `host` ADD COLUMN `pub_uuid` VARCHAR(40)  NOT NULL AFTER `u_u_id`;

CREATE OR REPLACE VIEW `SELINUX_ENABLED` AS select `host`.`selinux_enabled` AS `enabled`,count(`host`.`selinux_enabled`) AS `cnt` from `host` group by `host`.`selinux_enabled` order by count(`host`.`selinux_enabled`) desc;

CREATE OR REPLACE VIEW `SELINUX_ENFORCE` AS select `host`.`selinux_enforce` AS `enforce`,count(`host`.`selinux_enforce`) AS `cnt` from `host` group by `host`.`selinux_enforce` order by count(`host`.`selinux_enforce`) desc;

CREATE TABLE `file_systems` (
  `id` INT  NOT NULL AUTO_INCREMENT,
  `host_id` INT ,
  `mnt_pnt` VARCHAR(64) ,
  `fs_type` VARCHAR(16) ,
  `f_favail` INT ,
  `f_bsize` INT ,
  `f_frsize` INT ,
  `f_blocks` INT ,
  `f_bfree` INT ,
  `f_bavail` INT ,
  `f_files` INT ,
  `f_ffree` INT ,
  PRIMARY KEY (`id`),
  INDEX `host`(`host`)
)
ENGINE = MyISAM
CHARACTER SET utf8 COLLATE utf8_general_ci;

