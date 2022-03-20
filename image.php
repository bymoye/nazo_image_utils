<?php
/**
 * @Author: bymoye
 * @Date:   2022-03-20 18:47:30
 * @Last Modified by:   bymoye
 * @Last Modified time: 2022-03-20 20:18:10
 */
$json_string = file_get_contents('manifest.json');
$data = json_decode($json_string,True);
$keys = array_keys($data);
header('Content-Type: image/webp');
// 这里写点东西
readfile('webp/'.$keys[array_rand($keys)].'.source.webp');