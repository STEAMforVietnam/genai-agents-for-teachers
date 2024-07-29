from crewai_tools import tool


@tool("ExamHTMLMakerTool")
def create_exam_html_maker_tool(json_output):
    """
    This tool creates an html file from the JSON file
    """
    def compile_questions(self, question_sets, is_answer_key=False):
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

    def merge_all_sections(self, list_of_questions, list_of_tl):
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

    def exam_generation(self, question_sets, is_answer_key=False):
        list_of_questions, list_of_tl = self.compile_questions(question_sets, is_answer_key)
        html_content = self.merge_all_sections(list_of_questions, list_of_tl)
        return html_content
    print("DỮ LIỆU JSON TRẢ LẠI")
    print("===============")
    print(json_output)
    # exam_json_file = os.path.join(self.file_path, "./exam-in-progress.json")
    # exam_html_file = os.path.join(self.file_path, "./exam.html")
    # with open(exam_json_file, "r", encoding="utf-8") as file:
    #     question_sets = json.load(file)
    #     question_html = self.exam_generation(question_sets=question_sets)
    #     with open(exam_html_file, "w", encoding="utf-8") as exam:
    #         exam.write(question_html)

@tool("MatrixHTMLMakerTool")
def create_matrix_html_maker_tool(json_output):
    """
    This tool creates an html file from the JSON file
    """
    # TODO: bring all codes from https://github.com/STEAMforVietnam/Gen-AI-for-Teachers/blob/master/T%E1%BA%A1o-Ma-tr%E1%BA%ADn-%C4%90%E1%BB%81-b%C3%A0i/matrix-generation.ipynb 
    # and add here
    print("Gọi TOOL tạo Matrix")
    print("DỮ LIỆU JSON TRẢ LẠI")
    print("===============")
    print(json_output)
