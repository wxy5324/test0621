"""
数据处理后端 - 生成随机姓名和手机号
"""
import random
from typing import List, Dict, Any

# 常见姓氏
SURNAMES = [
    '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
    '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
    '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
    '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
]

# 常见名字用字（可组合成双字名）
GIVEN_CHARS = [
    '伟', '芳', '娜', '敏', '静', '强', '磊', '洋', '勇', '军',
    '杰', '娟', '艳', '涛', '明', '超', '秀', '霞', '平', '刚',
    '桂', '英', '华', '慧', '巧', '美', '丽', '云', '飞', '鑫',
    '宇', '峰', '阳', '波', '宁', '亮', '琳', '雪', '婷', '欣',
]

# 手机号号段（1开头，11位）
MOBILE_PREFIXES = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
                   '191', '198', '199']


def generate_random_contacts(n: int) -> List[Dict[str, Any]]:
    """
    生成 n 个随机姓名和手机号
    :param n: 数量，限制 1-500
    :return: [{"name": "张三", "phone": "13800138000"}, ...]
    """
    n = max(1, min(500, n))
    result = []
    seen_phones = set()

    for _ in range(n):
        # 随机姓名：单姓 + 1-2个字的名字
        surname = random.choice(SURNAMES)
        name_len = random.choice([1, 2])
        given = ''.join(random.choices(GIVEN_CHARS, k=name_len))
        name = surname + given

        # 随机手机号，避免重复
        while True:
            prefix = random.choice(MOBILE_PREFIXES)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(11 - len(prefix))])
            phone = prefix + suffix
            if phone not in seen_phones:
                seen_phones.add(phone)
                break

        result.append({'name': name, 'phone': phone})

    return result
