import requests
import re
import os


def main():
    path = r'C:\Users\Administrator\Desktop\题库'
    for fname in os.listdir(path):
        text = ''
        with open(path + '\\' + fname, encoding='utf-8', mode='r') as f:
            text = f.read()

        questions = re.findall(r'题：(.*?)\n', text)
        answers = re.findall(r'答案：(.*?)\n', text)
        counters = 0
        if len(questions) > len(answers):
            counters = len(answers)
        else:
            counters = len(questions)

        for i in range(counters):
            question = questions[i]
            options = answers[i]
            respon = requests.get(
                url='http://127.0.0.1:8000/makbank',
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                },
                params={
                    'classname': fname.replace('.txt', ''),
                    'question': question,
                    'options': options
                }
            )
            if respon:
                print(question, options)

        # def export(patten):
        #     for question, options in re.findall(patten, text):
        #
        #         #     for counter in range(len(questions)):
        #         #         question = questions[counter]
        #         #         options = answers[counter]
        #         respon = requests.get(
        #             url='http://127.0.0.1:8000/makbank',
        #             headers={
        #                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        #             },
        #             params={
        #                 'classname': fname.replace('.txt', ''),
        #                 'question': question,
        #                 'options': options
        #             }
        #         )
        #         if respon:
        #             print(respon.json())
        #
        # export(r'题：(.*?)\s*[选项.]*\s*答案：(\w*)\s*')
        # export(r'题：(.*?)\s*选项：.*\s*答案：(\w*)')


if __name__ == '__main__':
    main()
