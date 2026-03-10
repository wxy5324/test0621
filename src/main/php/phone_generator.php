<?php
/**
 * 根据起始手机号和数量，生成连续手机号数组
 * 用法：php phone_generator.php [起始手机号] [数量]
 * 示例：php phone_generator.php 15671557001 5
 * 或在浏览器访问：phone_generator.php?phone=15671557001&count=5
 */

function generatePhoneArray(string $startPhone, int $count): array {
    $phones = [];
    $base = (int) $startPhone;
    
    for ($i = 0; $i < $count; $i++) {
        $phones[] = (string) ($base + $i);
    }
    
    return $phones;
}

// 命令行模式
if (php_sapi_name() === 'cli') {
    $startPhone = $argv[1] ?? '15671557001';
    $count = (int) ($argv[2] ?? 5);
} else {
    // Web 模式
    $startPhone = $_GET['phone'] ?? '15671557001';
    $count = (int) ($_GET['count'] ?? 5);
}

$count = max(1, min($count, 1000));  // 限制 1-1000
$phones = generatePhoneArray($startPhone, $count);

// 输出格式：["15671557001","15671557002",...]
$output = json_encode($phones);

if (php_sapi_name() === 'cli') {
    echo $output . "\n";
} else {
    header('Content-Type: application/json; charset=utf-8');
    echo $output;
}
