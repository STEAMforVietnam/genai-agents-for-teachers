from typing import List, Dict
from crewai_tools import tool
from copy import deepcopy
from pprint import pprint
import json

def merge_learning_objects(existing_data, new_data):
    data = deepcopy(existing_data)
    for kl in data:
        for question_type in data[kl]:
            data[kl][question_type]['num_questions'] += int(new_data[kl][question_type]['num_questions'])
            data[kl][question_type]['total_score'] += int(new_data[kl][question_type]['total_score'])
    return data

def prepare_matrix_data(json_object):
    lo_data = {
        'knowing': {
            'multiple_choice': {
                'num_questions': 0,
                'total_score': 0
            },
            'free_form': {
                'num_questions': 0,
                'total_score': 0
            }
        },
        'understanding': {
            'multiple_choice': {
                'num_questions': 0,
                'total_score': 0
            },
            'free_form': {
                'num_questions': 0,
                'total_score': 0
            }
        },
        'application': {
            'multiple_choice': {
                'num_questions': 0,
                'total_score': 0
            },
            'free_form': {
                'num_questions': 0,
                'total_score': 0
            }
        },
        'adv_application': {
            'multiple_choice': {
                'num_questions': 0,
                'total_score': 0
            },
            'free_form': {
                'num_questions': 0,
                'total_score': 0
            }
        }
    }

    question_types = {
        'Trắc nghiệm': 'multiple_choice',
        'Tự luận': 'free_form'
    }

    knowledge_levels = {
        'Nhận biết': 'knowing',
        'Thông hiểu': 'understanding',
        'Vận dụng': 'application',
        'Vận dụng cao': 'adv_application'
    }

    matrix_data = {}

    for item in json_object:
        print("parsing json_object")
        chapter = item["topic"]
        learning_objective = item["sub_topic"]
        mastery_level = item["knowledge_level"]
        question_type = item["question_type"]
        question_num = int(item["number_of_questions"])
        total_score = int(item["total_points"])

        lo_question = deepcopy(lo_data)

        lo_question[knowledge_levels[mastery_level]][question_types[question_type]]['num_questions'] = question_num
        lo_question[knowledge_levels[mastery_level]][question_types[question_type]]['total_score'] = total_score

        if chapter not in matrix_data.keys():
            matrix_data[chapter] = {learning_objective: lo_question}
        else:
            if learning_objective not in matrix_data[chapter].keys():
                matrix_data[chapter][learning_objective] = lo_question
            else:
                matrix_data[chapter][learning_objective] = merge_learning_objects(matrix_data[chapter][learning_objective], lo_question)

    return matrix_data

def percentage_calculation(matrix_data):
    total = {
            'knowing': {
                'multiple_choice': {
                    'total_questions': 0,
                    'total_score': 0
                },
                'free_form': {
                    'total_questions': 0,
                    'total_score': 0
                }
            },
            'understanding': {
                'multiple_choice': {
                    'total_questions': 0,
                    'total_score': 0
                },
                'free_form': {
                    'total_questions': 0,
                    'total_score': 0
                }
            },
            'application': {
                'multiple_choice': {
                    'total_questions': 0,
                    'total_score': 0
                },
                'free_form': {
                    'total_questions': 0,
                    'total_score': 0
                }
            },
            'adv_application': {
                'multiple_choice': {
                    'total_questions': 0,
                    'total_score': 0
                },
                'free_form': {
                    'total_questions': 0,
                    'total_score': 0
                }
            }
        }

    for chapter in matrix_data.keys():
        for learning_objective in matrix_data[chapter].keys():
            for kl in matrix_data[chapter][learning_objective].keys():
                for question in matrix_data[chapter][learning_objective][kl].keys():
                    total[kl][question]['total_questions'] += matrix_data[chapter][learning_objective][kl][question]['num_questions']
                    total[kl][question]['total_score'] += matrix_data[chapter][learning_objective][kl][question]['total_score']

    return total

def generating_exam_matrix(matrix_json_obj, topic: str):
    title = f"MÔN {topic} - THỜI GIAN LÀM BÀI 90 PHÚT"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title></title>
        <style>
        html {
            font-size: 10px;
        }
        body {
            font-family: Georgia, Arial, Helvetica, sans-serif;
            font-size: 1.6rem;
        }
        h1 {
            font-size: 2rem;
            text-align: center;
            padding: 1rem 0;
        }
        table {
            width: 100%;
            border-style: solid;
            border-color:#000;
            border-width: 1px 0 0 1px;
            border-spacing: 0px;
        }
        td, th {
            border: 1px solid #000;
            border-width: 0 1px 1px 0;
            padding: .25rem .5rem;
        }
        thead th {
            background-color: #f0f0f0;
        }
        tbody td:first-child {
            text-align: left;
        }
        tfoot td {
            text-align: center;
            font-weight: bold;
            background-color: #f0f0f0;
        }

        .columnDataNumber {
            text-align: right;
        }
        .borderBottomDashed {
            border-bottom: 1px dashed #000;
        }
        </style>
        <meta name="description" content="" />
    </head>

    <body>
        <h1>
        MA TRẬN KIỂM TRA GIỮA HỌC KỲ I - NĂM HỌC 2023 - 2024
        <br>
        """ + title + """
        </h1>

        <!-- NOTE: The table has 14 columns -->
        <table>
        <thead>
            <tr>
            <th rowspan="3">TT</th>
            <th rowspan="3">Nội dung Kiến thức</th>
            <th rowspan="3">Đơn vị Kiến thức</th>
            <th colspan="8">Mức độ Nhận thức</th>
            <!-- <th></th>
            <th></th>
            <th></th>
            <th></th>
            <th></th>
            <th></th>
            <th></th> -->
            <th colspan="2">Tổng</th>
            <!-- <th></th> -->
            <th rowspan="3" class="columnDataNumber">Tổng điểm</th>
            </tr>
            <tr>
            <!-- <th rowspan="3">TT</th>
            <th rowspan="3">Nội dung Kiến thức</th>
            <th rowspan="3">Đơn vị Kiến thức</th> -->
            <th colspan="2">Nhận biết</th>
            <!--<th></th> -->
            <th colspan="2">Thông hiểu</th>
            <!--<th></th> -->
            <th colspan="2">Vận dụng</th>
            <!--<th></th> -->
            <th colspan="2">Vận dụng cao</th>
            <!--<th></th> -->
            <th colspan="2">Số câu hỏi</th>
            <!--<th></th> -->
            <!-- <th rowspan="3">Tổng điểm</th> -->
            </tr>
            <tr>
            <!-- <th rowspan="3">TT</th>
            <th rowspan="3">Nội dung Kiến thức</th>
            <th rowspan="3">Đơn vị Kiến thức</th> -->
            <th>TN</th>
            <th>TL</th>
            <th>TN</th>
            <th>TL</th>
            <th>TN</th>
            <th>TL</th>
            <th>TN</th>
            <th>TL</th>
            <th>TN</th>
            <th>TL</th>
            <!-- <th rowspan="3">Tổng điểm</th> -->
            </tr>
        </thead>
                <tbody>
            """
    matrix_data = prepare_matrix_data(matrix_json_obj)
    print("FINALLY creating HTML content")
    for seq, chapter in enumerate(matrix_data.keys()):
        html_content += f"""
        <tr>
    <td rowspan="{len(matrix_data[chapter]) * 2}">{seq + 1}</td>
    <td rowspan="{len(matrix_data[chapter]) * 2}">{chapter}</td>
        """
        for lo in matrix_data[chapter].keys():
            html_content += f"""
            <td rowspan="2">{lo}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['knowing']['multiple_choice']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['knowing']['free_form']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['understanding']['multiple_choice']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['understanding']['free_form']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['application']['multiple_choice']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['application']['free_form']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['adv_application']['multiple_choice']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{matrix_data[chapter][lo]['adv_application']['free_form']['num_questions']}</td>
            <td class="columnDataNumber borderBottomDashed">{sum([matrix_data[chapter][lo][level]['multiple_choice']['num_questions'] for level in ['knowing', 'understanding', 'application', 'adv_application']])}</td>
            <td class="columnDataNumber borderBottomDashed">{sum([matrix_data[chapter][lo][level]['free_form']['num_questions'] for level in ['knowing', 'understanding', 'application', 'adv_application']])}</td>
            <td class="columnDataNumber borderBottomDashed"></td>
            </tr>
            <tr>
            <!-- <td rowspan="4">1</td>
            <td rowspan="4">Căn bậc hai, căn bậc ba</td>
            <td rowspan="2">Căn bậc hai</td> -->
            <td class="columnDataNumber">{matrix_data[chapter][lo]['knowing']['multiple_choice']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['knowing']['free_form']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['understanding']['multiple_choice']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['understanding']['free_form']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['application']['multiple_choice']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['application']['free_form']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['adv_application']['multiple_choice']['total_score']}đ</td>
            <td class="columnDataNumber">{matrix_data[chapter][lo]['adv_application']['free_form']['total_score']}đ</td>
            <td class="columnDataNumber"></td>
            <td class="columnDataNumber"></td>
            <td class="columnDataNumber">{sum([matrix_data[chapter][lo][level]['multiple_choice']['total_score'] for level in ['knowing', 'understanding', 'application', 'adv_application']]) +  sum([matrix_data[chapter][lo][level]['free_form']['total_score'] for level in ['knowing', 'understanding', 'application', 'adv_application']])} </td>
            </tr>
            """
    total = percentage_calculation(matrix_data)

    total_score = sum([
        total[kl]['multiple_choice']['total_score'] for kl in
        ['knowing', 'understanding', 'application', 'adv_application']
    ]) + sum([
        total[kl]['free_form']['total_score'] for kl in
        ['knowing', 'understanding', 'application', 'adv_application']
    ])
    knowing_score = sum([
        total['knowing'][q]['total_score']
        for q in ['multiple_choice', 'free_form']
    ])
    understanding_score = sum([
        total['understanding'][q]['total_score']
        for q in ['multiple_choice', 'free_form']
    ])
    application_score = sum([
        total['application'][q]['total_score']
        for q in ['multiple_choice', 'free_form']
    ])
    adv_application_score = sum([
        total['adv_application'][q]['total_score']
        for q in ['multiple_choice', 'free_form']
    ])

    html_content += f"""
            </tbody>
            <tfoot>
            <tr>
            <td colspan="3">Tổng</td>
            <!-- <td></td>
            <td></td> -->
            <td class="columnDataNumber">{total['knowing']['multiple_choice']['total_questions']}</td>
            <td class="columnDataNumber">{total['knowing']['free_form']['total_questions']}</td>
            <td class="columnDataNumber">{total['understanding']['multiple_choice']['total_questions']}</td>
            <td class="columnDataNumber">{total['understanding']['free_form']['total_questions']}</td>
            <td class="columnDataNumber">{total['application']['multiple_choice']['total_questions']}</td>
            <td class="columnDataNumber">{total['application']['free_form']['total_questions']}</td>
            <td class="columnDataNumber">{total['adv_application']['multiple_choice']['total_questions']}</td>
            <td class="columnDataNumber">{total['adv_application']['free_form']['total_questions']}</td>
            <td class="columnDataNumber">{sum([total[kl]['multiple_choice']['total_questions'] for kl in ['knowing', 'understanding', 'application', 'adv_application']])}</td>
            <td class="columnDataNumber">{sum([total[kl]['free_form']['total_questions'] for kl in ['knowing', 'understanding', 'application', 'adv_application']])}</td>
            <td class="columnDataNumber">{total_score}</td>
            </tr>
            <tr>
            <td colspan="3">Tỷ lệ %</td>
            <!-- <td></td>
            <td></td> -->
            <td colspan="2">{knowing_score/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td colspan="2">{understanding_score/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td colspan="2">{application_score/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td colspan="2">{adv_application_score/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td colspan="2">{(knowing_score + understanding_score + application_score + adv_application_score)/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td class="columnDataNumber"></td>
            </tr>
            <tr>
            <td colspan="3">Tỷ lệ chung %</td>
            <!-- <td></td>
            <td></td> -->
            <td colspan="4">{(knowing_score + understanding_score)/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <!-- <td></td> -->
            <!-- <td></td> -->
            <td colspan="4">{(application_score + adv_application_score)/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <!-- <td></td> -->
            <!-- <td></td> -->
            <td colspan="2">{(knowing_score + understanding_score + application_score + adv_application_score)/total_score*100:.2f}%</td>
            <!-- <td></td> -->
            <td class="columnDataNumber"></td>
            </tr>
        </tfoot>
    </body>
    </html>
    """
    return html_content

@tool("ExamHTMLMakerTool")
def create_exam_html_maker_tool(input: Dict) -> str:
    """
    This tool creates an html file from the JSON file
    """
    def sort_questions(question_sets):
        """
        Sắp xếp các câu hỏi theo thứ tự Trắc nghiệm rồi đến Tự luận
        Đánh số lại theo đúng thứ tự
        """
        import random
        import operator
        items = list(question_sets.items())
        random.shuffle(items)

        question_sets_shuffled_sorted = []

        index = 1
        for item in items:
            item = list(item)
            item[0] = 'câu hỏi ' + str(index)
            if item[1].get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Trắc nghiệm":
                question_sets_shuffled_sorted.append(tuple(item))
                index += 1

        for item in items:
            item = list(item)
            item[0] = 'câu hỏi ' + str(index)
            if item[1].get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Tự luận":
                question_sets_shuffled_sorted.append(tuple(item))
                index += 1
        return dict(question_sets_shuffled_sorted)

    def compile_questions(question_sets, is_answer_key=False):
        """
        Trích câu hỏi, số điểm, và câu trả lời ra từ dữ liệu trong `question_sets`
        Nếu đang tạo file pdf cho bộ đề, để giá trị của is_answer_key = False
        Nếu đang tạo file pdf cho bài giải, để giá trị của is_answer_key = True
        """
        list_of_questions = ""
        list_of_tl = ""

        for key, value in question_sets.items():
            question_items = value.get('đề_bài').get('Nội dung').replace("\\n", "\n").replace("- A.", "A.").replace("- B.", "B.").replace("- C.", "C.").replace("- D.", "D.").split('\n')
            answer_choices = ""
            for ans in question_items[1:]:
                if ans:
                    answer_choices += fr"""<li><div class="marginLeft2">{ans}</div></li>"""


            question = fr"""<!-- A question: -->
                <article class="QuestionItem marginBottom2">
                <h3>
                    <strong><u>Câu {key.replace('câu ', '')}</u></strong>
                    <span>({value.get('đề_bài').get('Số điểm')} điểm): </span>
                    <span>{question_items[0]}</span>

                </h3>
                <ul class="QuestionItem-options columnNumbers4">
                {answer_choices}
                </ul>
                </article>
                <!-- /A question -->
                """.replace('\x08', '\\b')

            if is_answer_key:
                if value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Trắc nghiệm":
                  answer_key = fr"""<strong>Đáp Án: {value.get('đáp_án').get('Kết quả')}</strong>"""
                else:
                  trinh_bay = value.get('đáp_án').get('Trình bày').replace("\\n", "\n").replace(' \\\n ', ' \\\\\n ').replace(' \\\\ ', ' \\\\\n ').replace(' \\\\\ ', ' \\\\\n ').replace(' \\\ ', ' \\\\\n ')
                  answer_key = fr"""<strong>Đáp Án:</strong>""" + fr"""{trinh_bay}</strong>"""
                question += answer_key

            if value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Trắc nghiệm":
                list_of_questions += question
            elif value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Tự luận":
                list_of_tl += question

        return list_of_questions, list_of_tl

    def merge_all_sections(list_of_questions, list_of_tl):
        TEST_TMPL = """
        <!DOCTYPE html>
        <html>
            <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title></title>
            <script type="text/javascript" id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
            </script>
            <style>
                * {
                    box-sizing: border-box;
                }
                html {
                font-size: 10px;
                }
                body {
                font-family: 'Times New Roman', Times, serif;
                font-size: 1.6rem;
                }
                h1 {
                font-size: 2rem;
                text-align: center;
                margin: 0 0 .5rem;
                }
                h2, h3 {
                font-size: 1.6rem;
                font-weight: normal;
                margin-bottom: 0;
                }
                .container {
                width: 100%;
                max-width: 80rem;
                margin: 0 auto;
                padding: 2.4rem 1.6rem;
                }
                .marginLeft1 {
                margin-left: .25rem;
                }
                .marginLeft2 {
                margin-left: .5rem;
                }
                .marginBottom1 {
                margin-bottom: .5rem;
                }
                .marginBottom1 {
                margin-bottom: 1rem;
                }
                .marginBottom2 {
                margin-bottom: 1.5rem;
                }
                .marginBottom3 {
                margin-bottom: 3rem;
                }

                footer {
                text-align: center;
                }


                table {
                width: 100%;
                border-width: 0;
                border-spacing: 0px;
                }
                td {
                padding: .25rem .5rem;
                text-align: center;
                }

                .QuestionItem {}
                .QuestionItem-options {
                list-style-type: none;
                padding-left: 4.5rem;
                margin: 0;
                display: flex;
                flex-wrap: wrap;
                }
                .QuestionItem-options li {
                padding-right: 1.5rem;
                margin-top: 1rem;
                display: flex;
                }
                .QuestionItem-options li.isCorrectAnswer > strong {
                color: red;
                }

                .QuestionItem-options.columnNumbers1 li {
                width: 100%;
                }
                .QuestionItem-options.columnNumbers2 li {
                width: 50%;
                }
                .QuestionItem-options.columnNumbers3 li {
                width: 33.33%;
                }
                .QuestionItem-options.columnNumbers4 li {
                width: 25%;
                }


            </style>
            <meta name="description" content="" />
            </head>"""

        title = f"""<body>
            <div class="container">
                <header class="marginBottom3">
                    <table>
                        <tr>
                            <td>
                                <div>{province}</div>
                                <div><strong>{school}</strong></div>
                                <br>
                                <div><strong>Đề chính thức</strong></div>
                                <div><em>(Đề gồm 01 trang)</em></div>
                            </td>
                            <td>
                                <h1>{exam_name}</h1>
                                <div>
                                    <strong>Năm học: {year}</strong><br>
                                    <strong>Môn: {subject}</strong><br>
                                    <strong>Lớp: {class_year}</strong><br>
                                    <strong>Thời gian: {total_time} phút</strong>&nbsp;<em>(Không kể thời gian giao đề)</em>
                                </div>
                            </td>
                        </tr>
                    </table>
                </header>
        """

        part_1 = fr"""
                <main>
                    <!-- PART 1: TRẮC NGHIỆM -->
                    <section class="marginBottom3">
                        <h2>
                            <strong><u>I. Trắc nghiệm:</u></strong>
                            <strong class="marginLeft1"><em>Chọn câu trả lời đúng nhất trong các câu sau:</em></strong>
                        </h2>

                        {list_of_questions}

                    </section>"""
        part_2 = fr"""
                    <!-- PART 2: TỰ LUẬN -->
                    <section class="marginBottom3">
                        <h2>
                            <strong><u>II. Tự luận:</u></strong>
                        </h2>

                        {list_of_tl}

                    </section>
                </main>"""

        footer = """
                <footer>
                    <div><em>.............................Hết................................</em></div>
                    <div><em>Cán bộ coi thi không giải thích gì thêm!</em></div>
                </footer>
            </div>
        </html>"""
        return TEST_TMPL+title+part_1+part_2+footer

    def exam_generation(question_sets, is_answer_key=False):
        list_of_questions, list_of_tl = compile_questions(question_sets, is_answer_key)
        html_content = merge_all_sections(list_of_questions, list_of_tl)
        return html_content
    print("DỮ LIỆU JSON TRẢ LẠI")
    print("===============")
    print(json_output)

    question_sets_cleaned = {lesson.lower(): {k.lower().replace(" ", "_"): v for k, v in detail.items()}
                             for lesson, detail in input.items()}
    question_sets_cleaned_shuffled = sort_questions(question_sets_cleaned)
    question_html = exam_generation(question_sets_cleaned_shuffled)
    answer_key_html = exam_generation(question_sets_cleaned_shuffled, is_answer_key=True)
    
    with open("./exam.html", "w", encoding="utf-8") as exam:
        exam.write(question_html)

    with open("./answer_key.html", "w", encoding="utf-8") as exam_key:
        exam_key.write(answer_key_html)
    return "./exam.html"
    

@tool("MatrixHTMLMakerTool")
def create_matrix_html_maker_tool(input: List[Dict], topic: str) -> str:
    """
    This tool creates an html file from the JSON action input data
    Args:
        input (List[MatrixJSON]): is a list of dictionary. Each item in the list follow
        MatrixJSON structure. For example:
        [
            {'topic': 'test',
            'sub_topic': 'example',
            'knowledge_level': 'Nhận biết',
            'question_type': 'Trắc nghiệm',
            'number_of_questions': '4',
            'total_points': '40'}, 
            {'topic': 'Cơ học',
            'sub_topic': 'Động lực học',
            'knowledge_level': 'Thông hiểu',
            'question_type': 'Tự luận',
            'number_of_questions': '3',
            'total_points': '30'}
        ]
    """

    ### Write HTML
    html_content = generating_exam_matrix(input, topic)
    with open("./matrix.html", "w") as matrix:
        matrix.write(html_content)

    ### Write JSON
    with open('matrix.json', 'w') as f:
        json.dump(input, f)
    return "./matrix.html"
