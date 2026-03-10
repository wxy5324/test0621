"""
问题查询后端 - 从数据库执行 SQL 并返回结果
配置: 编辑 DB_CONFIG 或设置环境变量 DB_PASSWORD
"""
import os

# 数据库配置
DB_CONFIG = {
    'host': '10.16.4.15',
    'port': 3306,
    'user': 'qa_read',
    'password': 'QAread@2022',
    'database': 'redmine',
    'charset': 'utf8mb4',
}

ISSUE_SQL_BASE = """
SELECT
    iss.id AS id,
    ANY_VALUE(CASE
        WHEN iss.tracker_id = 1 THEN 'Bug'
        WHEN iss.tracker_id = 2 THEN 'Feature'
        WHEN iss.tracker_id = 3 THEN 'Support'
        ELSE 'Unknown'
    END) AS tracker,
    ANY_VALUE(sta.`name`) AS status,
    ANY_VALUE(iss.start_date) AS start_date,
    ANY_VALUE(iss.`subject`) AS subject,
    MAX(CASE WHEN cv.custom_field_id = 37 THEN cv.value END) AS class_info,
    ANY_VALUE(CONCAT(IFNULL(u.lastname,''), IFNULL(u.firstname,''))) AS assigned_to,
    MAX(CASE WHEN cv.custom_field_id = 16 THEN cv.value END) AS analysis
FROM issues iss
LEFT JOIN issue_statuses sta ON iss.status_id = sta.id
LEFT JOIN `users` u ON iss.assigned_to_id = u.id
LEFT JOIN custom_values cv
    ON iss.id = cv.customized_id
    AND cv.customized_type = 'Issue'
    AND cv.custom_field_id IN (37, 16)
WHERE
    iss.project_id = 348
    {date_clause}
GROUP BY iss.id
"""

COLUMN_NAMES = ['#', '跟踪', '状态', '开始日期', '主题', '上课信息', '指派给', '问题分析']
COLUMN_KEYS = ['id', 'tracker', 'status', 'start_date', 'subject', 'class_info', 'assigned_to', 'analysis']

# 线上问题查询 SQL - 项目 337,517,528,532,545,613
ONLINE_ISSUE_SQL_BASE = """
SELECT
    iss.id AS `#`,
    CASE
        WHEN iss.tracker_id = 1 THEN 'Bug'
        WHEN iss.tracker_id = 2 THEN 'Feature'
        WHEN iss.tracker_id = 3 THEN 'Support'
        ELSE 'Unknown'
    END AS `跟踪`,
    sta.`name` AS `状态`,
    enu.`name` AS `优先级`,
    p.`name` AS `项目`,
    MAX(CASE WHEN cv.custom_field_id = 18 THEN cv.value END) AS `系统模块`,
    iss.`subject` AS `主题`,
    MAX(CASE WHEN cv.custom_field_id = 19 THEN cv.value END) AS `问题原因`,
    MAX(CASE WHEN cv.custom_field_id = 29 THEN cv.value END) AS `问题类型`,
    MAX(CASE WHEN cv.custom_field_id = 30 THEN cv.value END) AS `问题级别`,
    MAX(CASE WHEN cv.custom_field_id = 21 THEN cv.value END) AS `反馈人`,
    MAX(CASE WHEN cv.custom_field_id = 23 THEN cv.value END) AS `反馈时间`,
    CONCAT(IFNULL(u.lastname,''), IFNULL(u.firstname,'')) AS `指派给`,
    MAX(CASE WHEN cv.custom_field_id = 24 THEN cv.value END) AS `研发负责人`,
    MAX(CASE WHEN cv.custom_field_id = 27 THEN cv.value END) AS `测试负责人`,
    MAX(CASE WHEN cv.custom_field_id = 26 THEN cv.value END) AS `处理时间`,
    MAX(CASE WHEN cv.custom_field_id = 31 THEN cv.value END) AS `持续时间(h)`
FROM issues iss
LEFT JOIN issue_statuses sta ON iss.status_id = sta.id
LEFT JOIN enumerations enu ON iss.priority_id = enu.id
LEFT JOIN projects p ON iss.project_id = p.id
LEFT JOIN `users` u ON iss.assigned_to_id = u.id
LEFT JOIN custom_values cv
    ON iss.id = cv.customized_id
    AND cv.customized_type = 'Issue'
    AND cv.custom_field_id IN (18,19,29,30,21,23,24,27,26,31)
WHERE iss.project_id IN (337,517,528,532,545,613)
    {date_clause}
GROUP BY
    iss.id, iss.tracker_id, sta.`name`, enu.`name`, p.`name`, iss.`subject`, u.lastname, u.firstname
"""

ONLINE_COLUMN_NAMES = ['#', '跟踪', '状态', '优先级', '项目', '系统模块', '主题', '问题原因', '问题类型', '问题级别', '反馈人', '反馈时间', '指派给', '研发负责人', '测试负责人', '处理时间', '持续时间(h)']


def fetch_issues(start_date=None, end_date=None):
    """
    执行问题查询 SQL，返回 {columns, rows} 或 {error}
    """
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError:
        return {'error': '请安装 pymysql: pip install pymysql'}

    try:
        cfg = dict(DB_CONFIG)
        if os.environ.get('DB_PASSWORD'):
            cfg['password'] = os.environ['DB_PASSWORD']
        conn = pymysql.connect(**cfg)
        cur = conn.cursor(DictCursor)

        date_clause = ''
        params = []
        if start_date and end_date:
            date_clause = 'AND iss.start_date BETWEEN %s AND %s'
            params = [start_date, end_date]
        elif start_date:
            date_clause = 'AND iss.start_date >= %s'
            params = [start_date]
        elif end_date:
            date_clause = 'AND iss.start_date <= %s'
            params = [end_date]

        sql = ISSUE_SQL_BASE.format(date_clause=date_clause)
        cur.execute(sql, params)
        raw = cur.fetchall()
        cur.close()
        conn.close()

        rows = []
        for r in raw:
            row = {}
            for i, key in enumerate(COLUMN_KEYS):
                v = r.get(key)
                if v is not None and hasattr(v, 'isoformat'):
                    v = v.isoformat()
                row[COLUMN_NAMES[i]] = v
            rows.append(row)
        return {'columns': COLUMN_NAMES, 'rows': rows}
    except Exception as e:
        return {'error': str(e)}


def fetch_online_issues(start_date=None, end_date=None):
    """
    执行线上问题查询 SQL，返回 {columns, rows} 或 {error}
    项目: 337,517,528,532,545,613
    """
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError:
        return {'error': '请安装 pymysql: pip install pymysql'}

    try:
        cfg = dict(DB_CONFIG)
        if os.environ.get('DB_PASSWORD'):
            cfg['password'] = os.environ['DB_PASSWORD']
        conn = pymysql.connect(**cfg)
        cur = conn.cursor(DictCursor)

        date_clause = ''
        params = []
        if start_date and end_date:
            date_clause = 'AND iss.start_date BETWEEN %s AND %s'
            params = [start_date, end_date]
        elif start_date:
            date_clause = 'AND iss.start_date >= %s'
            params = [start_date]
        elif end_date:
            date_clause = 'AND iss.start_date <= %s'
            params = [end_date]

        sql = ONLINE_ISSUE_SQL_BASE.format(date_clause=date_clause)
        cur.execute(sql, params)
        raw = cur.fetchall()
        cur.close()
        conn.close()

        rows = []
        for r in raw:
            row = {}
            for col in ONLINE_COLUMN_NAMES:
                v = r.get(col)
                if v is not None and hasattr(v, 'isoformat'):
                    v = v.isoformat()
                row[col] = v
            rows.append(row)
        return {'columns': ONLINE_COLUMN_NAMES, 'rows': rows}
    except Exception as e:
        return {'error': str(e)}
