@echo off
REM 二分插入排序单元测试运行脚本
REM 需要先下载 JUnit 4 和 Hamcrest 到 lib 目录:
REM   - junit-4.13.2.jar
REM   - hamcrest-core-1.3.jar

set LIB_DIR=lib
set CLASSPATH=.;%LIB_DIR%\junit-4.13.2.jar;%LIB_DIR%\hamcrest-core-1.3.jar

if not exist "%LIB_DIR%\junit-4.13.2.jar" (
    echo [错误] 未找到 JUnit，请将 junit-4.13.2.jar 和 hamcrest-core-1.3.jar 放入 lib 目录
    echo 下载地址: https://github.com/junit-team/junit4/releases
    exit /b 1
)

echo 编译...
javac -cp "%CLASSPATH%" BinaryInsertionSort.java BinaryInsertionSortTest.java
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo 运行测试...
java -cp "%CLASSPATH%" org.junit.runner.JUnitCore BinaryInsertionSortTest
exit /b %ERRORLEVEL%
