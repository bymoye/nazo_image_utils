<?php
/**
 * @Author: bymoye
 * @Date:   2022-03-20 18:47:30
 * @Last Modified by:   bymoye
 * @Last Modified time: 2022-03-20 20:35:00
 */
$json_string = file_get_contents('manifest.json');
$data = json_decode($json_string,True);
$keys = array_keys($data);
header('Content-Type: image/webp');
readfile('webp/'.$keys[array_rand($keys)].'.source.webp');