import os

import jieba
from collections import Counter
from pyecharts.charts import Bar
from pyecharts import options as opts
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 原始文本
text = """
随着全球人口增长和海洋资源需求的不断增加，海洋渔业在保障食品安全、促进经济发展方面发挥着重要作用。
然而，过度捕捞、海洋污染、生态破坏等问题日益严峻，影响了海洋生态系统的健康与稳定。
为了实现可持续发展，必须加强渔业管理、推进海洋保护区建设、推广生态养殖技术，
同时提升公众的环保意识，推动全球合作，实现资源共享与可持续利用。
"""

# 1. 中文分词
words = jieba.lcut(text)

# 2. 过滤停用词和标点符号
stopwords = ["，", "。", "、", "的", "在", "了", "和", "是", "随着", "不断", "方面", "重要", "作用",
             "然而", "日益", "影响", "与", "为了", "必须", "推进", "同时", "提升", "推动", "实现"]
filtered_words = [word for word in words if word not in stopwords and len(word) > 1]

# 3. 统计词频
word_counts = Counter(filtered_words)
top_words = word_counts.most_common(10)  # 取前10个高频词

# 4. 准备pyecharts数据
categories = [word[0] for word in top_words]
values = [word[1] for word in top_words]
total = sum(values)
percent_values = [round(v / total * 100, 1) for v in values]

# 5. 创建堆叠百分比条形图
bar = (
    Bar()
    .add_xaxis(categories)
    .add_yaxis("词频占比", percent_values, stack="stack1", category_gap="50%")
    .set_series_opts(
        label_opts=opts.LabelOpts(
            position="right",
            formatter="{b}: {c}%"
        )
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="文本词频统计(百分比堆叠图)"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            max_=100
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
    )
    .reversal_axis()
)


# 6. 生成词云 - 解决中文显示问题
# 获取系统中文字体路径
def get_chinese_font():
    try:
        # Windows系统
        if platform.system() == 'Windows':
            font_path = 'C:/Windows/Fonts/simhei.ttf'
            return font_path if os.path.exists(font_path) else None

        # Mac系统
        elif platform.system() == 'Darwin':
            font_path = '/System/Library/Fonts/STHeiti Medium.ttc'
            return font_path if os.path.exists(font_path) else None

        # Linux系统
        else:
            for font in fm.fontManager.ttflist:
                if 'SimHei' in font.name or 'Hei' in font.name or 'Song' in font.name:
                    return font.fname
            return None
    except:
        return None


# 设置中文字体
font_path = get_chinese_font()
if not font_path:
    # 如果找不到系统字体，尝试使用matplotlib的默认中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    font_path = None

word_freq = dict(top_words)
wc = WordCloud(
    font_path=font_path,  # 使用找到的中文字体
    width=800,
    height=600,
    background_color="white",
    max_words=200,
    max_font_size=100,
    random_state=42
)
wc.generate_from_frequencies(word_freq)

# 7. 显示结果
bar.render("word_freq_bar.html")  # 保存条形图为HTML文件

# 显示词云
plt.figure(figsize=(10, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("文本词云", fontproperties="SimHei")  # 确保标题也使用中文字体
plt.show()